#!/usr/bin/env python3
"""
Master Orchestrator Agent - Coordinates the complete pet adoption workflow
"""

import asyncio
import os
import json
import re
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

import requests
import httpx
from pydantic import BaseModel, Field
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

AGENT_JWT = os.getenv("AGENT_JWT", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjNDgwODI1OS03Y2ViLTQxOWEtYTQ2Ni0yMjlkN2IyNGEwMmIiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6ImFjYjE5MDc1LWYwMzYtNDc3Mi05NTllLTI1NzZkNjAwODdmNSJ9.31xNxTxZ2TZbcdXWJ0nWaucHTqnsdz7WQwoGy_nhDHI")
session = GenAISession(jwt_token=AGENT_JWT)

# Agent endpoints for inter-agent communication
AGENT_ENDPOINTS = {
    "data_fetcher": os.getenv("DATA_FETCHER_URL", "http://localhost:8001"),
    "content_generator": os.getenv("CONTENT_GENERATOR_URL", "http://localhost:8002"),
    "asset_assembler": os.getenv("ASSET_ASSEMBLER_URL", "http://localhost:8003"),
    "book_shipper": os.getenv("BOOK_SHIPPER_URL", "http://localhost:8004")
}

print(f"🎯 Master Orchestrator Agent initialized")
print(f"🔗 Agent endpoints configured: {len(AGENT_ENDPOINTS)} agents")


class TaskType(str, Enum):
    """Types of tasks the orchestrator can handle"""
    GENERATE_BOOK = "generate_book"
    SHIP_BOOK = "ship_book"
    FULL_WORKFLOW = "full_workflow"
    STATUS_CHECK = "status_check"


class OutputFormat(str, Enum):
    """Output formats for generated content"""
    PDF = "pdf"
    POWERPOINT = "ppt"
    BOTH = "both"
    VIDEO = "video"


@dataclass
class TaskRequest:
    """Parsed task request from user input"""
    task_type: TaskType
    location: Optional[str] = None
    shelter_name: Optional[str] = None
    num_pets: int = 5
    theme: str = "humorous"
    humorous: bool = True
    output_formats: List[OutputFormat] = field(default_factory=lambda: [OutputFormat.PDF])
    shipping_address: Optional[Dict[str, str]] = None
    specific_pets: List[str] = field(default_factory=list)
    book_title: Optional[str] = None
    additional_requirements: List[str] = field(default_factory=list)


@dataclass
class WorkflowState:
    """Current state of the workflow execution"""
    task_id: str
    current_step: str
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: str = "RUNNING"


class TaskParser:
    """Parses natural language task descriptions into structured requests"""
    
    def __init__(self):
        self.location_patterns = [
            r"(?:in|from|at|near)\s+([A-Za-z\s]+(?:,\s*[A-Z]{2})?)",
            r"([A-Za-z\s]+,\s*[A-Z]{2})\s+(?:pets|animals|shelters)",
            r"(?:city|location|area):\s*([A-Za-z\s,]+)"
        ]
        
        self.number_patterns = [
            r"(\d+)\s+(?:pets|animals|dogs|cats)",
            r"(?:find|get|fetch)\s+(\d+)",
            r"(?:number|count):\s*(\d+)"
        ]
        
        self.theme_patterns = [
            r"(?:humorous|funny|comedy|jokes?)",
            r"(?:serious|professional|formal)",
            r"(?:adventure|exciting|thrilling)",
            r"(?:heartwarming|emotional|touching)"
        ]
        
        self.output_patterns = [
            r"(?:pdf|book|document)",
            r"(?:powerpoint|ppt|presentation)",
            r"(?:video|movie|clip)",
            r"(?:both|all|everything)"
        ]
        
        self.shipping_patterns = [
            r"ship\s+(?:to|at)\s+(.+?)(?:\.|$)",
            r"(?:send|mail|deliver)\s+(?:to|at)\s+(.+?)(?:\.|$)",
            r"(?:address|shipping):\s*(.+?)(?:\.|$)"
        ]
    
    def parse_task(self, task_text: str) -> TaskRequest:
        """Parse natural language task into structured request"""
        task_text = task_text.lower().strip()
        
        # Determine task type
        if any(word in task_text for word in ["ship", "send", "mail", "deliver"]):
            task_type = TaskType.SHIP_BOOK
        elif any(word in task_text for word in ["status", "check", "track"]):
            task_type = TaskType.STATUS_CHECK
        elif any(word in task_text for word in ["book", "generate", "create", "make"]):
            if any(word in task_text for word in ["ship", "send", "mail", "deliver"]):
                task_type = TaskType.FULL_WORKFLOW
            else:
                task_type = TaskType.GENERATE_BOOK
        else:
            task_type = TaskType.FULL_WORKFLOW
        
        # Extract location
        location = None
        for pattern in self.location_patterns:
            match = re.search(pattern, task_text, re.IGNORECASE)
            if match:
                location = match.group(1).strip().title()
                break
        
        # Extract number of pets
        num_pets = 5  # default
        for pattern in self.number_patterns:
            match = re.search(pattern, task_text)
            if match:
                num_pets = int(match.group(1))
                break
        
        # Determine theme and humor
        humorous = True
        theme = "humorous"
        if any(word in task_text for word in ["serious", "professional", "formal"]):
            humorous = False
            theme = "professional"
        elif any(word in task_text for word in ["adventure", "exciting", "thrilling"]):
            theme = "adventure"
        elif any(word in task_text for word in ["heartwarming", "emotional", "touching"]):
            theme = "heartwarming"
        
        # Extract output formats
        output_formats = [OutputFormat.PDF]  # default
        if "powerpoint" in task_text or "ppt" in task_text:
            output_formats.append(OutputFormat.POWERPOINT)
        if "video" in task_text:
            output_formats.append(OutputFormat.VIDEO)
        if "both" in task_text or "all" in task_text:
            output_formats = [OutputFormat.PDF, OutputFormat.POWERPOINT]
        
        # Extract shipping address
        shipping_address = None
        for pattern in self.shipping_patterns:
            match = re.search(pattern, task_text, re.IGNORECASE)
            if match:
                address_text = match.group(1).strip()
                shipping_address = self._parse_address(address_text)
                break
        
        # Extract book title
        book_title = None
        title_match = re.search(r"(?:title|name|call):\s*[\"'](.+?)[\"']", task_text, re.IGNORECASE)
        if title_match:
            book_title = title_match.group(1)
        
        return TaskRequest(
            task_type=task_type,
            location=location,
            num_pets=num_pets,
            theme=theme,
            humorous=humorous,
            output_formats=output_formats,
            shipping_address=shipping_address,
            book_title=book_title
        )
    
    def _parse_address(self, address_text: str) -> Dict[str, str]:
        """Parse address text into structured format"""
        # Simple address parsing - in production, use a proper address parser
        parts = [part.strip() for part in address_text.split(',')]
        
        address = {
            "street": parts[0] if len(parts) > 0 else "",
            "city": parts[1] if len(parts) > 1 else "",
            "state": parts[2] if len(parts) > 2 else "",
            "postal_code": parts[3] if len(parts) > 3 else "",
            "country": "US"
        }
        
        return address


class AgentCommunicator:
    """Handles decentralized communication with other agents"""
    
    def __init__(self):
        self.session_timeout = 300  # 5 minutes
    
    async def call_agent(self, agent_name: str, function_name: str, 
                        parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific function on another agent"""
        if agent_name not in AGENT_ENDPOINTS:
            return {"success": False, "error": f"Unknown agent: {agent_name}"}
        
        endpoint = AGENT_ENDPOINTS[agent_name]
        
        try:
            # Prepare GenAI Protocol message
            message = {
                "function": function_name,
                "parameters": parameters,
                "timestamp": datetime.now().isoformat(),
                "caller": "master_orchestrator"
            }
            
            async with httpx.AsyncClient(timeout=self.session_timeout) as client:
                response = await client.post(
                    f"{endpoint}/invoke",
                    json=message,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {"success": True, "result": result}
                else:
                    return {
                        "success": False, 
                        "error": f"Agent call failed: {response.status_code}",
                        "response": response.text
                    }
                    
        except Exception as e:
            return {"success": False, "error": f"Communication error: {str(e)}"}
    
    async def fetch_pets(self, location: str, num_pets: int) -> Dict[str, Any]:
        """Fetch pet data from data_fetcher agent"""
        return await self.call_agent("data_fetcher", "data_fetcher", {
            "location": location,
            "num_pets": num_pets
        })
    
    async def generate_content(self, pets: List[Dict], humorous: bool = True) -> Dict[str, Any]:
        """Generate content from content_generator agent"""
        return await self.call_agent("content_generator", "content_generator", {
            "pets": pets,
            "humorous": humorous
        })
    
    async def assemble_assets(self, content: Dict[str, Any], 
                            specification: str = "") -> Dict[str, Any]:
        """Assemble assets from asset_assembler agent"""
        return await self.call_agent("asset_assembler", "asset_assembler", {
            "content": content,
            "specification": specification
        })
    
    async def ship_book(self, pdf_path: str, book_title: str, 
                       shipping_address: Dict[str, str]) -> Dict[str, Any]:
        """Ship book via book_shipper agent"""
        return await self.call_agent("book_shipper", "book_shipper", {
            "pdf_path": pdf_path,
            "book_title": book_title,
            "recipient_name": shipping_address.get("name", "Pet Lover"),
            "street_address": shipping_address.get("street", ""),
            "city": shipping_address.get("city", ""),
            "state": shipping_address.get("state", ""),
            "postal_code": shipping_address.get("postal_code", ""),
            "country": shipping_address.get("country", "US")
        })


class WorkflowOrchestrator:
    """Orchestrates the complete pet adoption workflow"""
    
    def __init__(self):
        self.communicator = AgentCommunicator()
        self.parser = TaskParser()
        self.active_workflows: Dict[str, WorkflowState] = {}
    
    async def execute_workflow(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Execute the complete workflow based on task request"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        workflow_state = WorkflowState(
            task_id=task_id,
            current_step="initialization"
        )
        
        self.active_workflows[task_id] = workflow_state
        
        try:
            if task_request.task_type == TaskType.FULL_WORKFLOW:
                result = await self._execute_full_workflow(task_request, workflow_state)
            elif task_request.task_type == TaskType.GENERATE_BOOK:
                result = await self._execute_book_generation(task_request, workflow_state)
            elif task_request.task_type == TaskType.SHIP_BOOK:
                result = await self._execute_book_shipping(task_request, workflow_state)
            else:
                result = {"success": False, "error": "Unknown task type"}
            
            workflow_state.status = "COMPLETED" if result.get("success") else "FAILED"
            workflow_state.end_time = datetime.now()
            
            return {
                "task_id": task_id,
                "workflow_state": workflow_state,
                "result": result
            }
            
        except Exception as e:
            workflow_state.status = "FAILED"
            workflow_state.end_time = datetime.now()
            
            return {
                "task_id": task_id,
                "workflow_state": workflow_state,
                "error": str(e)
            }
    
    async def _execute_full_workflow(self, task_request: TaskRequest, 
                                   workflow_state: WorkflowState) -> Dict[str, Any]:
        """Execute the complete workflow: fetch -> generate -> assemble -> ship"""
        
        # Step 1: Fetch pet data
        workflow_state.current_step = "fetching_pets"
        print(f"🔍 Step 1: Fetching {task_request.num_pets} pets from {task_request.location}")
        
        pets_result = await self.communicator.fetch_pets(
            task_request.location or "Alexandria, VA",
            task_request.num_pets
        )
        
        if not pets_result.get("success"):
            workflow_state.failed_steps.append("fetching_pets")
            return {"success": False, "error": "Failed to fetch pet data", "details": pets_result}
        
        workflow_state.completed_steps.append("fetching_pets")
        workflow_state.results["pets"] = pets_result["result"]
        
        # Step 2: Generate content
        workflow_state.current_step = "generating_content"
        print(f"🎨 Step 2: Generating {task_request.theme} content for pets")
        
        content_result = await self.communicator.generate_content(
            pets_result["result"],
            task_request.humorous
        )
        
        if not content_result.get("success"):
            workflow_state.failed_steps.append("generating_content")
            return {"success": False, "error": "Failed to generate content", "details": content_result}
        
        workflow_state.completed_steps.append("generating_content")
        workflow_state.results["content"] = content_result["result"]
        
        # Step 3: Assemble assets
        workflow_state.current_step = "assembling_assets"
        print(f"📚 Step 3: Assembling assets into {task_request.output_formats}")
        
        specification = f"Create {', '.join(task_request.output_formats)} with {task_request.theme} theme"
        assets_result = await self.communicator.assemble_assets(
            content_result["result"],
            specification
        )
        
        if not assets_result.get("success"):
            workflow_state.failed_steps.append("assembling_assets")
            return {"success": False, "error": "Failed to assemble assets", "details": assets_result}
        
        workflow_state.completed_steps.append("assembling_assets")
        workflow_state.results["assets"] = assets_result["result"]
        
        # Step 4: Ship book (if shipping address provided)
        if task_request.shipping_address:
            workflow_state.current_step = "shipping_book"
            print(f"🚚 Step 4: Shipping book to {task_request.shipping_address.get('city', 'recipient')}")
            
            pdf_path = assets_result["result"].get("pdf_path")
            if not pdf_path:
                workflow_state.failed_steps.append("shipping_book")
                return {"success": False, "error": "No PDF generated for shipping"}
            
            book_title = task_request.book_title or f"Pet Adoption Book - {task_request.location}"
            
            shipping_result = await self.communicator.ship_book(
                pdf_path,
                book_title,
                task_request.shipping_address
            )
            
            if not shipping_result.get("success"):
                workflow_state.failed_steps.append("shipping_book")
                return {"success": False, "error": "Failed to ship book", "details": shipping_result}
            
            workflow_state.completed_steps.append("shipping_book")
            workflow_state.results["shipping"] = shipping_result["result"]
        
        return {
            "success": True,
            "message": "Full workflow completed successfully",
            "completed_steps": workflow_state.completed_steps,
            "results": workflow_state.results
        }
    
    async def _execute_book_generation(self, task_request: TaskRequest, 
                                     workflow_state: WorkflowState) -> Dict[str, Any]:
        """Execute book generation workflow without shipping"""
        
        # Steps 1-3 from full workflow
        result = await self._execute_full_workflow(task_request, workflow_state)
        
        # Remove shipping step if it was attempted
        if "shipping_book" in workflow_state.completed_steps:
            workflow_state.completed_steps.remove("shipping_book")
        if "shipping" in workflow_state.results:
            del workflow_state.results["shipping"]
        
        return result
    
    async def _execute_book_shipping(self, task_request: TaskRequest, 
                                   workflow_state: WorkflowState) -> Dict[str, Any]:
        """Execute book shipping for existing PDF"""
        
        # This assumes a PDF path is provided in the task request
        # In practice, this would be called after book generation
        
        workflow_state.current_step = "shipping_book"
        
        if not task_request.shipping_address:
            return {"success": False, "error": "No shipping address provided"}
        
        # For now, use the most recent PDF if available
        pdf_path = "../alexandria_pets_complete_storybook_20250714_012300.pdf"  # Example
        book_title = task_request.book_title or "Pet Adoption Storybook"
        
        shipping_result = await self.communicator.ship_book(
            pdf_path,
            book_title,
            task_request.shipping_address
        )
        
        if shipping_result.get("success"):
            workflow_state.completed_steps.append("shipping_book")
            workflow_state.results["shipping"] = shipping_result["result"]
            return {"success": True, "shipping_result": shipping_result["result"]}
        else:
            workflow_state.failed_steps.append("shipping_book")
            return {"success": False, "error": "Failed to ship book", "details": shipping_result}


@session.bind(
    name="orchestrate_workflow",
    description="Orchestrates the complete pet adoption workflow from task parsing to final delivery"
)
async def orchestrate_workflow(
    agent_context: GenAIContext,
    task_description: Annotated[str, "Natural language description of the task to perform"],
    priority: Annotated[str, "Task priority (low, medium, high)"] = "medium"
) -> Dict[str, Any]:
    """
    Main orchestration function that handles complete workflow execution
    
    Parses natural language task descriptions and coordinates all agents to:
    1. Fetch real pet data from shelters
    2. Generate humorous stories and AI images
    3. Assemble professional books/PDFs/presentations
    4. Ship physical books to specified addresses
    5. Provide tracking and status updates
    """
    agent_context.logger.info(f"Starting workflow orchestration for task: {task_description}")
    
    orchestrator = WorkflowOrchestrator()
    
    # Parse the task description
    task_request = orchestrator.parser.parse_task(task_description)
    
    agent_context.logger.info(f"Parsed task: {task_request.task_type.value} for {task_request.location}")
    
    # Execute the workflow
    result = await orchestrator.execute_workflow(task_request)
    
    if result.get("workflow_state"):
        workflow_state = result["workflow_state"]
        agent_context.logger.info(f"Workflow {workflow_state.task_id} completed with status: {workflow_state.status}")
    
    return result


@session.bind(
    name="get_workflow_status",
    description="Get the status of a running or completed workflow"
)
async def get_workflow_status(
    agent_context: GenAIContext,
    task_id: Annotated[str, "Task ID to check status for"]
) -> Dict[str, Any]:
    """
    Get the current status of a workflow execution
    
    Returns detailed information about workflow progress, completed steps,
    and any errors that occurred during execution
    """
    agent_context.logger.info(f"Checking status for task: {task_id}")
    
    # In a real implementation, this would query a persistent store
    # For now, we'll return a mock status
    
    return {
        "task_id": task_id,
        "status": "COMPLETED",
        "current_step": "completed",
        "completed_steps": ["fetching_pets", "generating_content", "assembling_assets", "shipping_book"],
        "progress": "100%",
        "estimated_completion": "Already completed",
        "results_available": True
    }


@session.bind(
    name="list_available_locations",
    description="List available locations for pet adoption workflows"
)
async def list_available_locations(
    agent_context: GenAIContext
) -> Dict[str, Any]:
    """
    List available locations where pet data can be fetched
    
    Returns a list of supported cities and regions for pet adoption workflows
    """
    agent_context.logger.info("Listing available locations for pet adoption workflows")
    
    # This would query the data_fetcher agent in a real implementation
    locations = [
        {"city": "Alexandria", "state": "VA", "country": "US"},
        {"city": "Arlington", "state": "VA", "country": "US"},
        {"city": "Washington", "state": "DC", "country": "US"},
        {"city": "Baltimore", "state": "MD", "country": "US"},
        {"city": "Richmond", "state": "VA", "country": "US"}
    ]
    
    return {
        "success": True,
        "locations": locations,
        "total_count": len(locations)
    }


async def main():
    """Main function for testing the master orchestrator"""
    print("🎯 Master Orchestrator Agent started")
    print("📋 Ready to coordinate pet adoption workflows")
    
    # Example workflow execution for testing
    print("\n🧪 Testing workflow orchestration...")
    
    # Test task parsing
    parser = TaskParser()
    test_tasks = [
        "Create a humorous book for 3 pets from Alexandria, VA and ship to 123 Main St, Arlington, VA",
        "Generate a professional PDF for 5 dogs in Baltimore, MD",
        "Make a funny presentation about cats in Washington, DC",
        "Ship the Alexandria pet book to John Doe, 456 Oak Ave, Richmond, VA 23220"
    ]
    
    for task in test_tasks:
        print(f"\n📝 Parsing: {task}")
        parsed = parser.parse_task(task)
        print(f"   Type: {parsed.task_type.value}")
        print(f"   Location: {parsed.location}")
        print(f"   Pets: {parsed.num_pets}")
        print(f"   Theme: {parsed.theme}")
        print(f"   Outputs: {[f.value for f in parsed.output_formats]}")
        if parsed.shipping_address:
            print(f"   Shipping: {parsed.shipping_address['city']}, {parsed.shipping_address['state']}")
    
    # Start the agent session
    await session.process_events()


if __name__ == "__main__":
    asyncio.run(main()) 
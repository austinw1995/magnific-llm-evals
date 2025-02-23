from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from magnific import LLMConfig, OpenAIProvider, LLMConversation, TestRunner, Evaluation
from magnific.synthetic_data import SyntheticDataGenerator, SyntheticDataConfig

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RerunRequest(BaseModel):
    config: Dict[str, Any]
    test_results: List[Dict[str, Any]]

class GenerateSyntheticDataRequest(BaseModel):
    service_prompt: str
    model: str
    num_tests: int = Field(default=5, le=100)  # Limit to 100 tests max
    max_threads: int = Field(default=5, le=10)  # Limit to 10 threads max
    temperature: float = Field(default=0.8, ge=0, le=2.0)

@app.post("/api/rerun")
async def rerun_evaluations(request: RerunRequest):
    try:
        # Create test runner
        runner = TestRunner(eval_model=request.config["params"]["model"])
        
        # Initialize list to store all conversations
        all_conversations = []
        
        # Create conversations for each test result
        for test in request.test_results:
            # Configure service provider with new config
            service_config = LLMConfig(
                params=request.config["params"],
                system_prompt=request.config["system_prompt"],
                end_call_enabled=request.config["end_call_enabled"]
            )
            
            # Keep original customer config
            customer_config = LLMConfig(**test["customer_config"])
            
            # Create conversation
            conversation = LLMConversation(
                service_provider=OpenAIProvider(config=service_config),
                customer_provider=OpenAIProvider(config=customer_config),
                type=test["call_type"],
                first_message=test["transcript"].split("\n\n")[1].split(": ")[1],
                evaluations=[
                    Evaluation(name=result["name"], prompt=result["reason"]) 
                    for result in test["evaluation_results"]
                ]
            )
            
            all_conversations.append(conversation)
        
        # Run all tests
        results = await runner.run_tests(conversations=all_conversations, max_turns=20)
        
        return {"success": True, "results": results}
        
    except Exception as e:
        import traceback
        print(f"Error in rerun_evaluations: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-synthetic")
async def generate_synthetic_data(request: GenerateSyntheticDataRequest):
    try:
        config = SyntheticDataConfig(
            service_prompt=request.service_prompt,
            model=request.model,
            num_tests=request.num_tests,
            max_threads=request.max_threads,
            temperature=request.temperature
        )
        
        generator = SyntheticDataGenerator(config)
        scenarios = await generator.generate()
        
        return {
            "success": True,
            "scenarios": scenarios
        }
        
    except Exception as e:
        import traceback
        print(f"Error generating synthetic data: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e)) 
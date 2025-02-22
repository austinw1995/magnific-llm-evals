import asyncio
from typing import List, Dict, Any, Optional
from magnific.conversation import LLMConversation
from magnific.evaluators.evalrunner import LlmEvaluator
from magnific.evaluators.evaluator import save_results_to_csv, EvaluationResult
from pathlib import Path

class TestResult:
    def __init__(self, test_id: int, call_type: str, transcript: str, evaluation_results: List[Dict], 
                 service_config: Dict, customer_config: Dict):
        self.test_id = test_id
        self.call_type = call_type
        self.transcript = transcript
        self.evaluation_results = evaluation_results
        self.service_config = service_config
        self.customer_config = customer_config

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "call_type": self.call_type,
            "transcript": self.transcript,
            "evaluation_results": self.evaluation_results,
            "service_config": {
                "params": self.service_config["params"],
                "system_prompt": self.service_config["system_prompt"],
                "end_call_enabled": self.service_config["end_call_enabled"]
            },
            "customer_config": {
                "params": self.customer_config["params"],
                "system_prompt": self.customer_config["system_prompt"],
                "end_call_enabled": self.customer_config["end_call_enabled"]
            }
        }

class TestRunner:
    def __init__(self, eval_model: str = "gpt-4o-mini"):
        self.eval_model = eval_model
        self.test_counter = 0  # Initialize counter for test IDs

    async def run_tests(
        self, 
        conversations: List[LLMConversation], 
        max_turns: int = 20,
        save_logs: bool = True,
        logs_dir: Optional[Path] = None
    ) -> Dict[str, Dict]:
        # Create tasks for all conversations sequentially
        async with asyncio.TaskGroup() as tg:
            tasks = []
            for conv in conversations:
                self.test_counter += 1  # Increment counter before creating each task
                tasks.append(
                    tg.create_task(self.run_single_test(conv, self.test_counter, max_turns))
                )
        
        # Collect results
        results = {
            task.result().test_id: task.result().to_dict()
            for task in tasks
        }
        
        # Save results to CSV if requested
        if save_logs:
            for test_id, result in results.items():
                # Convert the evaluation results back to EvaluationResult objects
                eval_results = [
                    EvaluationResult(**eval_dict)
                    for eval_dict in result["evaluation_results"]
                ]
                
                # Save to CSV
                save_results_to_csv(
                    model_type="LLM",
                    model_name=result["service_config"]["params"].get("model", "unknown"),
                    transcript=result["transcript"],
                    evaluation_results=eval_results,
                    logs_dir=logs_dir
                )
        
        return results

    async def run_single_test(self, conversation: LLMConversation, test_id: str, max_turns: int = 20) -> TestResult:
        # Run conversation
        conversation.have_conversation(max_turns=max_turns)
        
        # Create a new evaluator for this test
        evaluator = LlmEvaluator(model=self.eval_model)
        
        # Evaluate results
        eval_response = await evaluator.evaluate(conversation)
        evaluation_results = eval_response.evaluation_results if eval_response else []
        
        # Get configurations from providers
        service_config = {
            "params": conversation.service_provider.config.params,
            "system_prompt": conversation.service_provider.config.system_prompt,
            "end_call_enabled": conversation.service_provider.config.end_call_enabled
        }
        
        customer_config = {
            "params": conversation.customer_provider.config.params,
            "system_prompt": conversation.customer_provider.config.system_prompt,
            "end_call_enabled": conversation.customer_provider.config.end_call_enabled
        }
        
        return TestResult(
            test_id=test_id,
            call_type=conversation.type,
            transcript=conversation.transcript,
            evaluation_results=[result.dict() for result in evaluation_results],
            service_config=service_config,
            customer_config=customer_config
        )
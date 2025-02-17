import asyncio
from typing import List, Dict, Any
from magnific.conversation import LLMConversation
from magnific.evaluators.evalrunner import LlmEvaluator
import uuid

class TestResult:
    def __init__(self, test_id: str, call_type: str, transcript: str, evaluation_results: List[Dict]):
        self.test_id = test_id
        self.call_type = call_type
        self.transcript = transcript
        self.evaluation_results = evaluation_results

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "call_type": self.call_type,
            "transcript": self.transcript,
            "evaluation_results": self.evaluation_results
        }

class TestRunner:
    def __init__(self, eval_model: str = "gpt-4o-mini"):
        self.eval_model = eval_model

    async def run_single_test(self, conversation: LLMConversation, max_turns: int = 20) -> TestResult:
        # Run conversation
        conversation.have_conversation(max_turns=max_turns)
        
        # Create a new evaluator for this test
        evaluator = LlmEvaluator(model=self.eval_model)
        
        # Evaluate results
        eval_response = await evaluator.evaluate(conversation)
        evaluation_results = eval_response.evaluation_results if eval_response else []
        
        # Create unique test ID
        test_id = str(uuid.uuid4())
        
        return TestResult(
            test_id=test_id,
            call_type=conversation.type,
            transcript=conversation.transcript,
            evaluation_results=[result.dict() for result in evaluation_results]
        )

    async def run_tests(self, conversations: List[LLMConversation], max_turns: int = 20) -> Dict[str, Dict]:
        # Create tasks for all conversations
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(self.run_single_test(conv, max_turns))
                for conv in conversations
            ]
        
        # Collect results
        results = {
            task.result().test_id: task.result().to_dict()
            for task in tasks
        }
        
        return results 
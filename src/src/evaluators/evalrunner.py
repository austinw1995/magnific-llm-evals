import os
from typing import List, Optional
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from evaluators.evaluator import BaseEvaluator, EvaluationResponse, EvaluationResult
from src.evaluation import Evaluation
import asyncio
from src.conversation import LLMConversation

class LlmEvaluator(BaseEvaluator):
    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY") or "")
        self.model = model
    
    async def evaluate(self, conversation: LLMConversation) -> Optional[EvaluationResponse]:
        """Evaluate a call locally.
        """
        transcript = conversation.transcript
        evaluations = conversation.evaluations
        results = []
        
        # Create all tasks at once
        tasks = [
            self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"Evaluate the following transcript for this specific criterion:\n{evaluation.__dict__}\nProvide a score between 0 and 1, where 1 is perfect and 0 is complete failure."},
                    {"role": "user", "content": f"Transcript:\n{str(transcript)}"}
                ],
                temperature=0,
                max_tokens=100,
                response_format=EvaluationResult,
            )
            for evaluation in evaluations
        ]
        
        # Run all tasks in parallel
        responses = await asyncio.gather(*tasks)
        results = [r.choices[0].message.parsed for r in responses]
        if results is None:
            return None
        return EvaluationResponse(evaluation_results=results)
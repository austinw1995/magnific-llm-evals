import os
from typing import List, Optional
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from magnific.evaluators.evaluator import BaseEvaluator, EvaluationResponse, EvaluationResult
import asyncio
from magnific.conversation import LLMConversation
import json

class LlmEvaluator(BaseEvaluator):
    def __init__(self, model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY") or "")
        self.model = model
    
    async def evaluate(self, conversation: LLMConversation) -> Optional[EvaluationResponse]:
        """Evaluate a call locally."""
        transcript = conversation.transcript
        evaluations = conversation.evaluations
        
        system_prompt = """You are an evaluator. Your task is to analyze transcripts and provide structured evaluations.

You must respond with ONLY a JSON object in the following format, with no additional text or explanation:
{
    "score": <float between 0.0 and 1.0>,
    "passed": <true if score >= 0.7, false otherwise>,
    "reason": "<detailed explanation for the score>"
}

Rules:
1. score must be a decimal number between 0.0 and 1.0 (1.0 is perfect, 0.0 is complete failure)
2. passed must be a boolean (true/false) based on whether score >= 0.7
3. reason must be a clear explanation justifying the score
4. Response must contain ONLY the JSON object - no other text
5. JSON must use double quotes and exact key names as shown above"""

        # Create all tasks at once
        tasks = [
            self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Evaluate this transcript for: {evaluation.prompt}\n\nTranscript:\n{transcript}"}
                ],
                temperature=0,
                max_tokens=10000
            )
            for evaluation in evaluations
        ]
        
        # Run all tasks in parallel
        responses = await asyncio.gather(*tasks)
        
        results = []
        for i, response in enumerate(responses):
            try:
                # Parse JSON from response
                result_dict = json.loads(response.choices[0].message.content)
                # Create EvaluationResult with the evaluation name
                result = EvaluationResult(
                    name=evaluations[i].name,
                    score=float(result_dict["score"]),
                    passed=bool(result_dict["passed"]),
                    reason=str(result_dict["reason"])
                )
                results.append(result)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Error parsing evaluation result: {e}")
                # Provide a default result if parsing fails
                results.append(EvaluationResult(
                    name=evaluations[i].name,
                    score=0.0,
                    passed=False,
                    reason=f"Failed to parse evaluation result: {str(e)}"
                ))
        
        return EvaluationResponse(evaluation_results=results)
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, Field
from dataclasses import dataclass

class EvaluationResult(BaseModel):
    name: str
    passed: bool
    score: float = Field(description="A score between 0 and 1")
    reason: str

class EvaluationResponse(BaseModel):
    evaluation_results: List[EvaluationResult]

class BaseEvaluator(ABC):
    @abstractmethod
    async def evaluate(self, transcript: str, evaluations: List[Any]) -> EvaluationResponse:
        """Evaluate a conversation transcript based on given evaluation criteria"""
        raise NotImplementedError
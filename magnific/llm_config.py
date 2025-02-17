from dataclasses import dataclass, field
from typing import Dict

@dataclass
class LLMConfig:
    """Base configuration class for LLM providers"""
    system_prompt: str
    params: Dict = field(default_factory=dict)
    end_call_enabled: bool = False 
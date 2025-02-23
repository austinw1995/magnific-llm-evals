import asyncio
from typing import List, Dict, Any
from openai import AsyncOpenAI
import json
from dataclasses import dataclass
from magnific.llm_config import LLMConfig
import math

@dataclass
class SyntheticDataConfig:
    service_prompt: str
    model: str
    num_tests: int
    max_threads: int = 5
    temperature: float = 0.8

class SyntheticDataGenerator:
    def __init__(self, config: SyntheticDataConfig):
        self.config = config
        self.client = AsyncOpenAI()
        
        self.system_prompt = """You are a synthetic data generator for customer service scenarios. Your task is to create diverse customer profiles and their initial messages for testing a customer service agent.

For each customer, provide a JSON object in the following format:
{
    "type": "<inbound or outbound>",
    "customer_prompt": "<system prompt for the customer agent>",
    "first_message": "<initial message from the customer>",
    "description": "<brief description of the customer persona and their situation>"
}

Consider diverse customer types:
1. Different emotional states (frustrated, happy, neutral, concerned)
2. Various issue complexities (simple queries to complex problems)
3. Different communication styles (direct, verbose, technical, non-technical)
4. Diverse backgrounds and needs
5. Different levels of urgency

The customer_prompt should follow this template:
"You are a customer <context>.
Your tone is <emotional state>.
Try to <objective>.
IMPORTANT: Use the tool end_call() only when you are satisfied with <success condition>."

Respond with an array of JSON objects, each representing a unique customer scenario."""

    async def _generate_batch(self, batch_size: int) -> List[Dict[str, Any]]:
        """Generate a batch of synthetic customer configs"""
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"""Given this service agent prompt:

{self.config.service_prompt}

Generate {batch_size} diverse customer scenarios that would interact with this service agent. 
Make sure the scenarios are realistic and test different aspects of the service agent's capabilities.
Ensure the customer prompts align with the service context while maintaining diversity in customer needs and behaviors."""}
                ],
                temperature=self.config.temperature,
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"Error generating batch: {e}")
            return []

    async def generate(self) -> List[Dict[str, Any]]:
        """Generate synthetic customer configurations"""
        # Calculate number of batches needed (max 10 scenarios per batch)
        batch_size = 10
        num_batches = math.ceil(self.config.num_tests / batch_size)
        scenarios_per_batch = min(batch_size, self.config.num_tests)
        
        # Create batches with limited concurrency
        all_scenarios = []
        for i in range(0, num_batches, self.config.max_threads):
            batch_tasks = []
            for j in range(min(self.config.max_threads, num_batches - i)):
                remaining = self.config.num_tests - len(all_scenarios)
                if remaining <= 0:
                    break
                current_batch_size = min(scenarios_per_batch, remaining)
                batch_tasks.append(self._generate_batch(current_batch_size))
            
            if batch_tasks:
                batch_results = await asyncio.gather(*batch_tasks)
                for scenarios in batch_results:
                    all_scenarios.extend(scenarios)
                    if len(all_scenarios) >= self.config.num_tests:
                        break
        
        return all_scenarios[:self.config.num_tests] 
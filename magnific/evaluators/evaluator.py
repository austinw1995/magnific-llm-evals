from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, Field
from dataclasses import dataclass
import os
from pathlib import Path
from datetime import datetime
import csv
import json

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

def get_default_logs_dir() -> Path:
    """Get the default logs directory (./logs relative to project root)."""
    current_file_dir = Path(__file__).parent
    project_root = current_file_dir.parent.parent  # Go up two levels to reach project root
    return project_root / "logs"

def save_results_to_csv(
    model_type: str,
    model_name: str,
    transcript: str,
    evaluation_results: List[EvaluationResult],
    logs_dir: Optional[Union[str, Path]] = None,
    filename: Optional[str] = None
) -> Path:
    """
    Save evaluation results to a CSV file in the logs directory.
    
    Args:
        model_type: The type of the model (e.g., 'gpt', 'claude')
        model_name: The name of the model
        transcript: The evaluated transcript
        evaluation_results: List of EvaluationResult objects
        logs_dir: Optional custom logs directory path
        filename: Optional custom filename (default: evaluation_results_YYYY-MM-DD.csv)
    
    Returns:
        Path to the created CSV file
    """
    # Set up logs directory
    logs_path = Path(logs_dir) if logs_dir else get_default_logs_dir()
    logs_path.mkdir(parents=True, exist_ok=True)
    
    # Generate default filename if none provided
    if filename is None:
        # Add timestamp to the date
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"evaluation_results_{timestamp}.csv"
    
    output_file = logs_path / filename
    
    # Prepare the row data
    row_data = {
        'Type': model_type,
        'Name': model_name,
        'Transcript': transcript,
    }
    
    # Add scores with their corresponding eval names
    for result in evaluation_results:
        row_data[f'Score_{result.name}'] = result.score

    # Check if file exists to determine if we need to write headers
    file_exists = output_file.exists()
    
    with output_file.open(mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=list(row_data.keys()))
        
        # Write headers only if file is new
        if not file_exists:
            writer.writeheader()
            
        writer.writerow(row_data)
    
    return output_file

def save_test_details_to_json(
    test_id: str,
    model_type: str,
    model_name: str,
    transcript: str,
    evaluation_results: List[EvaluationResult],
    service_config: Dict,
    customer_config: Dict,
    logs_dir: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Save complete test details including configs to a JSON file.
    """
    logs_path = Path(logs_dir) if logs_dir else get_default_logs_dir()
    logs_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    json_filename = f"test_details_{test_id}_{timestamp}.json"
    output_file = logs_path / json_filename
    
    test_data = {
        'test_id': test_id,
        'model_type': model_type,
        'model_name': model_name,
        'timestamp': timestamp,
        'transcript': transcript,
        'evaluation_results': [result.dict() for result in evaluation_results],
        'service_config': service_config,
        'customer_config': customer_config
    }
    
    with output_file.open('w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2)
    
    return output_file

def save_run_details_to_json(
    test_results: Dict[str, Dict],
    logs_dir: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Save all test results from a single run to one JSON file.
    """
    logs_path = Path(logs_dir) if logs_dir else get_default_logs_dir()
    logs_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    json_filename = f"run_details_{timestamp}.json"
    output_file = logs_path / json_filename
    
    run_data = {
        'timestamp': timestamp,
        'tests': test_results
    }
    
    with output_file.open('w', encoding='utf-8') as f:
        json.dump(run_data, f, indent=2)
    
    return output_file
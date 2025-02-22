export interface EvaluationRow {
  id: number;
  type: string;
  name: string;
  transcript: string;
  scores: number[];
}

export interface ModelConfig {
  params: {
    model: string;
    temperature: number;
    max_tokens: number;
  };
  system_prompt: string;
  end_call_enabled: boolean;
}

export interface TestResult {
  test_id: number;
  call_type: string;
  transcript: string;
  evaluation_results: Array<{
    name: string;
    passed: boolean;
    score: number;
    reason: string;
  }>;
  service_config: ModelConfig;
  customer_config: ModelConfig;
}

export interface RunDetails {
  timestamp: string;
  tests: {
    [key: string]: TestResult;
  };
}
# Magnific-Evals

A python package for testing LLMs specifically for voice agents under customer service scenarios.

## Installation

```bash
pip install magnific-llm-evals
```

This will automatically install all required dependencies.

Alternatively, if installing from source:
```bash
git clone https://github.com/austinw1995/magnific-llm-evals
cd magnific-llm-evals
pip install -r requirements.txt
```

## Features

- Evaluate multiple LLMs against various customer conversation scenarios by customizing the service and customer agents
- Define custom evaluation criteria for a successful conversation
- Run multiple tests in parallel and record conversation transcripts
- Generate detailed evaluation reports

## Usage

First, set up your API keys depending on what LLMs you want to test.
```
os.environ["OPENAI_API_KEY"] = "..."
os.environ["ANTHROPIC_API_KEY"] = "..."
os.environ["TOGETHER_API_KEY"] = "..."
os.environ["GROQ_API_KEY"] = "..."
os.environ["DEEPSEEK_API_KEY"] = "..."
os.environ["XAI_API_KEY"] = "..."
os.environ["GEMINI_API_KEY"] = "..."
```

We support a variety of LLMs through 7 providers, which are OpenAI, Anthropic, TogetherAI, Groq, DeepSeek, Cerebrad, XAI, and Google Gemini:
You can access different models through different providers with
```
from magnific import (
    OpenAIProvider,
    AnthropicProvider,
    TogetherAIProvider,
    GroqProvider,
    DeepSeekProvider,
    CerebrasProvider,
    XAIProvider,
    GeminiProvider,
)
```
For each provider, the following models are supported:
| Provider              | Models |
|-----------------------|--------|
| **OpenAIProvider**    | gpt-4o<br>gpt-4o-mini<br>gpt-3.5-turbo-0125<br>o1<br>o1-mini<br>o3-mini |
| **AnthropicProvider** | claude-3-5-sonnet-20241022<br>claude-3-5-haiku-20241022<br>claude-3-opus-20240229<br>claude-3-sonnet-20240229<br>claude-3-haiku-20240307 |
| **TogetherAIProvider**| meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo<br>meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo<br>meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo<br>meta-llama/Llama-3.3-70B-Instruct-Turbo<br>mistralai/Mixtral-8x7B-Instruct-v0.1<br>mistralai/Mistral-7B-Instruct-v0.1<br>Qwen/Qwen2.5-7B-Instruct-Turbo<br>Qwen/Qwen2.5-72B-Instruct-Turbo |
| **GroqProvider**      | qwen-2.5-32b<br>deepseek-r1-distill-qwen-32b<br>deepseek-r1-distill-llama-70b<br>llama-3.3-70b-versatile<br>llama-3.1-8b-instant<br>mixtral-8x7b-32768<br>gemma2-9b-it |
| **DeepSeekProvider**  | deepseek-chat<br>deepseek-reasoner |
| **CerebrasProvider**  | llama3.1-8b<br>llama-3.3-70b<br>DeepSeek-R1-Distill-Llama-70B |
| **XAIProvider**       | xgrok-2-latest |
| **GeminiProvider**    | gemini-2.0-flash<br>gemini-2.0-flash-lite-preview-02-05<br>gemini-1.5-flash<br>gemini-1.5-flash-8b<br>gemini-1.5-pro |

To set the configuration for a service or customer agent, create a LLMConfig object with the desired parameters.
1. params is a dictionary of any parameter supported by the LLM model provider.
2. system_prompt is the instruction task for the LLM agent to follow.
3. end_call_enabled is a boolean that determines if the LLM should be able to end the call with the function call end_call(). (Note: IMPORTANT texts are highlighted in the system prompt to ensure function call reliability).

```
service_config_1 = LLMConfig(
        params={
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 150,
        },
        system_prompt="""You are a voice assistant for Vappy's Pizzeria, a pizza shop located on the Internet...IMPORTANT: Do not use tool end_call() until all of the customer's questions are answered and they say something like "bye" or "see you.''
""",
        end_call_enabled=True
    )

service_config_2 = LLMConfig(
        params={
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.2,
            "max_tokens": 90,
        },
        system_prompt="""You are a voice assistant for Vappy's Burgers, a burger shop located on the Internet...IMPORTANT: Do not use tool end_call() until all of the customer's questions are answered and they say something like "bye" or "see you.'
""",
        end_call_enabled=True
    )

customer_config_1 = LLMConfig(
        params={
            "model": "gemini-2.0-flash"
        },
        system_prompt="""You are a hungry customer who wants to order food...IMPORTANT: Use the tool end_call() only when you are satisfied with your order and all your questions are answered.
""",
        end_call_enabled=True
    )

customer_config_2 = LLMConfig(
        params={
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.9,
            "max_tokens": 50,
        },
        system_prompt="""You are a cheerful customer who wants to order food...IMPORTANT: Use the tool end_call() only when you are satisfied with your order and all your questions are answered.
""",
        end_call_enabled=True
    )
```

To instantiate a list of conversations for testing, use the LLMConversation class.
1. type is the type of conversation, either "inbound" or "outbound", inbound is the customer calling in and outbound is the service agent calling out.
2. first_message is the first message in the conversation by the caller.
3. evaluations is a list of user defined evaluations to be performed on the conversation, customize the name of the evaluation and prompt, which specifies the evaluation criteria.

```
conversations = [
        LLMConversation(
            service_provider=OpenAIProvider(config=service_config_1),
            customer_provider=GeminiProvider(config=customer_config_1),
            type="inbound",
            first_message="Hi, what's on the menu today?",
            evaluations=[
                Evaluation(name="Menu", prompt="The menu should be displayed in a structured format, with each item on a new line."),
                Evaluation(name="helpfulness", prompt="The service agent should be helpful and answer all questions.")
            ]
        ),
        LLMConversation(
            service_provider=AnthropicProvider(config=service_config_2),
            customer_provider=GroqProvider(config=customer_config_2),
            type="outbound",
            first_message="Hi, what would you like to order?",
            evaluations=[
                Evaluation(name="Menu", prompt="The menu should be displayed in a structured format, with each item on a new line."),
                Evaluation(name="conciseness", prompt="The service agent should be concise.")
            ]
        ),
        LLMConversation(
            service_provider=OpenAIProvider(config=service_config_1),
            customer_provider=GeminiProvider(config=customer_config_1),
            type="inbound",
            first_message="Hi, I'm so hungry",
            evaluations=[
                Evaluation(name="empathy", prompt="The service agent should be empathetic and show understanding of the customer's situation."),
                Evaluation(name="frustration", prompt="The customer should not be frustrated or annoyed.")
            ]
        )
    ]
```

Finally, to run the tests in parallel, with the evaluation criterias (for eval models we only support openai for now), use the TestRunner class.

```
runner = TestRunner(eval_model="gpt-4o-mini")
results = await runner.run_tests(conversations)
```

The results will be a dictionary with the test_id as the key and the test result as the value.
An example result based on the conversations above is shown below, where the evaluations output scores and reasons for passing or failing. The transcript, as well as the LLM configurations of service and customer agents are also included in the result for prompt management purposes.

```
{
  "1": {
    "test_id": 1,
    "call_type": "inbound",
    "transcript": "...",
    "evaluation_results": [
      {
        "name": "Menu",
        "passed": false,
        "score": 0.2,
        "reason": "The menu items are mentioned in a conversational format rather than a structured format with each item on a new line. The response does not meet the requirement for clear presentation."
      },
      {
        "name": "helpfulness",
        "passed": true,
        "score": 1.0,
        "reason": "The service agent provided detailed information about the menu items, answered all questions asked by the customer, and offered additional options, demonstrating a high level of helpfulness."
      }
    ],
    "service_config": {
      "params": {
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 150
      },
      "system_prompt": "You are a voice assistant for Vappy's Pizzeria...",
      "end_call_enabled": true
    },
    "customer_config": {
      "params": {
        "model": "claude-3-5-sonnet-20241022",
        "temperature": 0.9,
        "max_tokens": 100
      },
      "system_prompt": "You are a hungry customer who wants to order food...",
      "end_call_enabled": true
    }
  },
  "2": {
    "test_id": 2,
    "call_type": "outbound",
    "transcript": "...",
    "evaluation_results": [
      {
        "name": "Menu",
        "passed": true,
        "score": 1.0,
        "reason": "The menu items were clearly listed in a structured format, with each item on a new line, making it easy to read and understand."
      },
      {
        "name": "conciseness",
        "passed": true,
        "score": 0.8,
        "reason": "The service agent provided clear and relevant information without unnecessary elaboration. However, there were moments where the responses could have been slightly more succinct, particularly in confirming the order."
      }
    ],
    "service_config": {
      "params": {
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 150
      },
      "system_prompt": "You are a voice assistant for Vappy's Pizzeri...",
      "end_call_enabled": true
    },
    "customer_config": {
      "params": {
        "model": "claude-3-5-sonnet-20241022",
        "temperature": 0.9,
        "max_tokens": 100
      },
      "system_prompt": "You are a hungry customer who wants to order food...",
      "end_call_enabled": true
    }
  },
  "3": {
    "test_id": 3,
    "call_type": "inbound",
    "transcript": "...",
    "evaluation_results": [
      {
        "name": "empathy",
        "passed": true,
        "score": 0.9,
        "reason": "The service agent demonstrated a good level of empathy by responding positively to the customer's excitement about food and acknowledging their hunger. However, there could have been more explicit expressions of understanding or concern for the customer's situation."
      },
      {
        "name": "frustration",
        "passed": true,
        "score": 1.0,
        "reason": "The customer expressed excitement and eagerness throughout the conversation, showing no signs of frustration or annoyance."
      }
    ],
    "service_config": {
      "params": {
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 150
      },
      "system_prompt": "You are a voice assistant for Vappy's Pizzeria...",
      "end_call_enabled": true
    },
    "customer_config": {
      "params": {
        "model": "claude-3-5-sonnet-20241022",
        "temperature": 0.9,
        "max_tokens": 100
      },
      "system_prompt": "You are a hungry customer who wants to order food...",
      "end_call_enabled": true
    }
  }
}
```

More examples can be found in the examples folder.
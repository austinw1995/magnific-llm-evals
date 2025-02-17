import os
import asyncio
from magnific import LLMConfig
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
from magnific import LLMConversation
from magnific import Evaluation
from magnific import TestRunner

async def main():
    os.environ["OPENAI_API_KEY"] = "..."
    os.environ["ANTHROPIC_API_KEY"] = "..."
    os.environ["GROQ_API_KEY"] = "..."
    os.environ["GEMINI_API_KEY"] = "..."
    # Configure service agent
    service_config_1 = LLMConfig(
        params={
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 150,
        },
        system_prompt="""You are a voice assistant for Vappy's Pizzeria, a pizza shop located on the Internet.
Your job is to take the order of customers calling in. The menu has only 3 types of items: pizza, sides, and drinks.
Keep responses short and simple. Do not end the call until the customer says bye.
IMPORTANT: Do not use tool end_call() until all of the customer's questions are answered and they say something like "bye" or "see you.'
""",
        end_call_enabled=True
    )

    service_config_2 = LLMConfig(
        params={
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.2,
            "max_tokens": 90,
        },
        system_prompt="""You are a voice assistant for Vappy's Burgers, a burger shop located on the Internet.
Your job is to take the order of customers calling in. The menu has only 3 types of items: burgers, sides, and milkshakes.
Keep responses short and simple. Do not end the call until the customer says bye.
IMPORTANT: Do not use tool end_call() until all of the customer's questions are answered and they say something like "bye" or "see you.'
""",
        end_call_enabled=True
    )
    
    # Configure customer agent with different parameters
    customer_config_1 = LLMConfig(
        params={
            "model": "gemini-2.0-flash"
        },
        system_prompt="""You are a hungry customer who wants to order food.
Your tone is casual and excited.
IMPORTANT: Use the tool end_call() only when you are satisfied with your order and all your questions are answered.
""",
        end_call_enabled=True
    )

    customer_config_2 = LLMConfig(
        params={
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.9,
            "max_tokens": 50,
        },
        system_prompt="""You are a cheerful customer who wants to order food.
Your tone is cheerful and excited.
IMPORTANT: Use the tool end_call() only when you are satisfied with your order and all your questions are answered.
""",
        end_call_enabled=True
    )
    
    # Create list of conversations to test
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

    # Run all tests with a specific evaluation model
    runner = TestRunner(eval_model="gpt-4o-mini")
    results = await runner.run_tests(conversations)

    # Print results
    for test_id, result in results.items():
        print(f"\nTest ID: {test_id}")
        print(f"Call Type: {result['call_type']}")
        print("\nTranscript:")
        print(result['transcript'])
        print("\nEvaluation Results:")
        for eval_result in result['evaluation_results']:
            print(f"\n{eval_result['name']}:")
            print(f"Score: {eval_result['score']}")
            print(f"Passed: {eval_result['passed']}")
            print(f"Reason: {eval_result['reason']}")

    print(results)

if __name__ == "__main__":
    asyncio.run(main())
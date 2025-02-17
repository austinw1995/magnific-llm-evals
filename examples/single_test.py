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
    os.environ["OPENAI_API_KEY"] = "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"

    # Configure service agent
    service_config = LLMConfig(
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
    
    # Configure customer agent with different parameters
    customer_config = LLMConfig(
        params={
            "model": "gpt-4o-mini"
        },
        system_prompt="""You are a hungry customer who wants to order food.
Your tone is casual and excited.
IMPORTANT: Use the tool end_call() only when you are satisfied with your order and all your questions are answered.
""",
        end_call_enabled=True
    )

    # Create list of conversations to test
    conversations = [
        LLMConversation(
            service_provider=OpenAIProvider(config=service_config),
            customer_provider=OpenAIProvider(config=customer_config),
            type="inbound",
            first_message="Hi, what's on the menu today?",
            evaluations=[
                Evaluation(name="Menu", prompt="The menu should be displayed in a structured format, with each item on a new line."),
                Evaluation(name="helpfulness", prompt="The service agent should be helpful and answer all questions.")
            ]
        )
    ]

    # Run all tests with a specific evaluation model
    runner = TestRunner(eval_model="gpt-4o")
    results = await runner.run_tests(conversations, max_turns=20)

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
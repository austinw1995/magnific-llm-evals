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
    os.environ["ANTHROPIC_API_KEY"] = "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"
    os.environ["TOGETHER_API_KEY"] = "tgp_v1_kgOJIMtsAYusUYc9pcmB-jWHoJg35GJxU00JfeNWjwk"
    os.environ["GROQ_API_KEY"] = "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"
    os.environ["DEEPSEEK_API_KEY"] = "sk-997610731f454ff7a6837fd67998b17e"
    os.environ["XAI_API_KEY"] = "xai-PjaCbaSlEpu53VxlmKHPXki5iCSrLKQoYEGn9ijURo0O96Q7YJrHvIv2abDUfWbnLJ8yqvb17EP9zcYt"
    os.environ["GEMINI_API_KEY"] = "AIzaSyBJwBl-HFFh4nfGgQBPNchM2r3tzayGO2M"

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
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.9,
            "max_tokens": 100,
        },
        system_prompt="""You are a hungry customer who wants to order food.
Your tone is casual and excited.
IMPORTANT: Use the tool end_call() only when you are satisfied with your order and all your questions are answered.
""",
        end_call_enabled=True
    )
    
    # Create providers with custom configs
    service_provider = OpenAIProvider(config=service_config)
    customer_provider = AnthropicProvider(config=customer_config)
    
    # Create list of conversations to test
    conversations = [
        LLMConversation(
            service_provider=service_provider,
            customer_provider=customer_provider,
            type="inbound",
            first_message="Hi, what's on the menu today?",
            evaluations=[
                Evaluation(name="Menu", prompt="The menu should be displayed in a structured format, with each item on a new line."),
                Evaluation(name="helpfulness", prompt="The service agent should be helpful and answer all questions.")
            ]
        ),
        LLMConversation(
            service_provider=service_provider,
            customer_provider=customer_provider,
            type="outbound",
            first_message="Hi, what would you like to order?",
            evaluations=[
                Evaluation(name="Menu", prompt="The menu should be displayed in a structured format, with each item on a new line."),
                Evaluation(name="conciseness", prompt="The service agent should be concise.")
            ]
        ),
        LLMConversation(
            service_provider=service_provider,
            customer_provider=customer_provider,
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
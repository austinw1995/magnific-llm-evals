import asyncio
import os
from dotenv import load_dotenv
from magnific import LLMConfig, OpenAIProvider, LLMConversation, TestRunner, Evaluation

# Load environment variables
load_dotenv()

# OpenAI models to test
MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
]

# Example conversation configurations
CONVERSATIONS = [
    {
        "type": "inbound",
        "customer_prompt": """You are a customer contacting customer service about a delayed delivery.
Your tone is frustrated but polite.
Try to get information about your package and compensation for the delay.
IMPORTANT: Use the tool end_call() only when you are satisfied with your order and all your questions are answered.""",
        
        "service_prompt": """You are a customer service representative for an e-commerce company.
Be professional, empathetic, and helpful. Follow these guidelines:
1. Always verify order details first
2. Explain shipping delays honestly
3. Offer appropriate compensation when necessary
4. Maintain a positive and professional tone
IMPORTANT: Do not use tool end_call() until all of the customer's questions are answered and they say something like "bye" or "see you."""
    },
    {
        "type": "outbound",
        "customer_prompt": """You are a customer having issues with your laptop.
Your tone is concerned but cooperative.
Try to get help fixing your laptop issues.
IMPORTANT: Use the tool end_call() only when you are satisfied with the support and all your questions are answered.""",
        
        "service_prompt": """You are a technical support representative.
Help customers diagnose and resolve their technical issues.
Follow these steps:
1. Gather basic device information
2. Ask about specific symptoms
3. Guide through basic troubleshooting
4. Escalate if necessary
IMPORTANT: Do not use tool end_call() until all of the customer's questions are answered and they say something like "bye" or "see you."""
    }
]

async def run_tests():
    # Create test runner
    runner = TestRunner(eval_model="gpt-4o")
    
    # Initialize list to store all conversations
    all_conversations = []
    
    # Create conversations for each model and scenario
    for model in MODELS:
        for conv_config in CONVERSATIONS:
            # Configure service provider (using the current model)
            service_config = LLMConfig(
                params={
                    "model": model,
                    "temperature": 0.7,
                },
                system_prompt=conv_config["service_prompt"],
                end_call_enabled=True
            )
            
            # Configure customer (using a consistent model)
            customer_config = LLMConfig(
                params={
                    "model": "gpt-4o",
                    "temperature": 0.7,
                },
                system_prompt=conv_config["customer_prompt"],
                end_call_enabled=True
            )
            
            # Create conversation with specific first messages based on type
            first_message = "Hi, what's on the menu today?" if conv_config["type"] == "inbound" else "Hi, what would you like to order?"
            
            conversation = LLMConversation(
                service_provider=OpenAIProvider(config=service_config),
                customer_provider=OpenAIProvider(config=customer_config),
                type=conv_config["type"],
                first_message=first_message,
                evaluations=[
                    Evaluation(name="empathy", prompt="The service agent should be empathetic and show understanding of the customer's situation."),
                    Evaluation(name="helpfulness", prompt="The service agent should be helpful and provide clear solutions."),
                    Evaluation(name="frustration", prompt="The customer should not be frustrated or annoyed.")
                ]
            )
            
            all_conversations.append(conversation)
    
    # Run all tests
    results = await runner.run_tests(conversations=all_conversations, max_turns=20)
    
    # Print summary
    print("\nTest Results Summary:")
    print("=" * 50)
    for test_id, result in results.items():
        print(f"\nTest {test_id}:")
        print(f"Model: {result['service_config']['params']['model']}")
        print(f"Type: {result['call_type']}")
        print("Evaluation Scores:")
        for eval_result in result["evaluation_results"]:
            print(f"- {eval_result['name']}: {eval_result['score']:.2f}")
        print("-" * 30)

if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    # Run tests
    asyncio.run(run_tests()) 
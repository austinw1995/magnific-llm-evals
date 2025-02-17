from typing import List, Dict
from magnific.llm_providers import LLMProvider
from dataclasses import field
from magnific.evaluation import Evaluation

class LLMConversation:
    def __init__(self, 
                 service_provider: LLMProvider,
                 customer_provider: LLMProvider,
                 type: str = "inbound",
                 first_message: str = "Hi, I'd like to order a pizza",
                 evaluations: List[Evaluation] = None):
        self.service_provider = service_provider
        self.customer_provider = customer_provider
        self.type = type
        self.evaluations = evaluations if evaluations is not None else []
        
        # Initialize conversation based on type
        if self.type == "inbound":
            self.first_speaker = "customer_agent"
            self.second_speaker = "service_agent"
            self.first_provider = self.customer_provider
            self.second_provider = self.service_provider
        else:
            self.first_speaker = "service_agent"
            self.second_speaker = "customer_agent"
            self.first_provider = self.service_provider
            self.second_provider = self.customer_provider
            
        self.conversation_history = [{"speaker": self.first_speaker, "content": first_message}]
        self.call_active = True
        self.transcript = ""  # Initialize empty transcript

    def end_call(self):
        """This function can be called by the LLM to end the conversation."""
        self.call_active = False

    def get_conversation_from_perspective(self, speaker: str) -> List[Dict]:
        """
        Transcribe conversation history from the perspective of the given speaker.
        For each LLM, their own messages are seen as 'assistant' and the other LLM's as 'user'.
        """
        perspective_history = []
        for message in self.conversation_history:
            role = "assistant" if message["speaker"] == speaker else "user"
            perspective_history.append({
                "role": role,
                "content": message["content"]
            })
        return perspective_history

    def get_llm_response(self, provider: LLMProvider, speaker: str) -> str:
        messages = [{"role": "system", "content": provider.config.system_prompt}]
        messages.extend(self.get_conversation_from_perspective(speaker))
        
        try:
            message_content, end_call_detected = provider.get_completion(messages, provider.config.end_call_enabled)
            if end_call_detected:
                self.end_call()
                return "Thank you, bye."
            return message_content
        except Exception as e:
            print(f"Error getting LLM response: {e}")
            return ""

    def have_conversation(self, max_turns: int = 3):
        # Start the transcript with conversation type
        self.transcript = f"Starting {self.type} conversation\n\n"
        self.transcript += f"{self.first_speaker}: {self.conversation_history[0]['content']}\n\n"
        #print(self.transcript, end="")
        
        turn = 0
        while self.call_active and turn < max_turns:
            # Second speaker's turn
            response1 = self.get_llm_response(self.second_provider, self.second_speaker)
            self.conversation_history.append({"speaker": self.second_speaker, "content": response1})
            self.transcript += f"{self.second_speaker}: {response1}\n\n"
            #print(f"{self.second_speaker}: {response1}\n")
            #time.sleep(0.2)
            if not self.call_active:
                end_message = f"Conversation ended via end_call() function by {self.second_speaker}."
                self.transcript += end_message + "\n"
                #print(end_message)
                break

            # First speaker's turn
            response2 = self.get_llm_response(self.first_provider, self.first_speaker)
            self.conversation_history.append({"speaker": self.first_speaker, "content": response2})
            self.transcript += f"{self.first_speaker}: {response2}\n\n"
            #print(f"{self.first_speaker}: {response2}\n")
            #time.sleep(0.2)
            if not self.call_active:
                end_message = f"Conversation ended via end_call() function by {self.first_speaker}."
                self.transcript += end_message + "\n"
                #print(end_message)
                break
            
            turn += 1
            
        return self.transcript
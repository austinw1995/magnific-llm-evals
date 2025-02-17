from openai import OpenAI
from anthropic import Anthropic
from groq import Groq
from cerebras.cloud.sdk import Cerebras
from google import genai
from google.genai import types
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import os
from src.llm_config import LLMConfig

class LLMProvider(ABC):
    @abstractmethod
    def get_completion(self, messages: List[Dict], end_call_enabled: bool = True, tools: Optional[List[Dict]] = None) -> tuple[str, Optional[Dict]]:
        """Get completion from LLM provider
        Returns: (message_content, tool_call)"""
        pass

class OpenAIProvider(LLMProvider):
    #The following models are supported:
    #gpt-4o
    #gpt-4o-mini
    #gpt-3.5-turbo-0125
    #o1
    #o1-mini
    #o3-mini
    def __init__(self, config: LLMConfig):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.config = config
        
    def get_completion(
            self,
            messages: List[Dict],
            end_call_enabled: bool = True,
            tools: Optional[List[Dict]] = None
    ) -> tuple[str, Optional[Dict]]:
        # Create a new tools list for this call
        current_tools = [] if tools is None else tools.copy()
        
        params = {
            "messages": messages,
            **self.config.params
        }
        
        if end_call_enabled:
            current_tools.append({
                "type": "function",
                "function": {
                    "name": "end_call",
                    "description": "Ends the conversation by deactivating the active call.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    },
                    "strict": True
                }
            })
            
        if current_tools:
            params["tools"] = current_tools
            
        response = self.client.chat.completions.create(**params)
        message_content = response.choices[0].message.content
        tool_calls = response.choices[0].message.tool_calls or []  # Default to empty list if None
        
        end_call_detected = False
        for tool_call in tool_calls:
            if tool_call.function.name == "end_call":
                end_call_detected = True
                break

        return message_content, end_call_detected

class AnthropicProvider(LLMProvider):
    #The following models are supported:
    #claude-3-5-sonnet-20241022
    #claude-3-5-haiku-20241022
    #claude-3-opus-20240229
    #claude-3-sonnet-20240229
    #claude-3-haiku-20240307
    def __init__(self, config: LLMConfig):
        self.client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.config = config
        
    def get_completion(self,
                       messages: List[Dict],
                       end_call_enabled: bool = True,
                       tools: Optional[List[Dict]] = None
    ) -> tuple[str, Optional[Dict]]:
        # Create a new tools list for this call
        current_tools = [] if tools is None else tools.copy()
        
        # Extract system message and convert remaining messages
        system_message = next((m["content"] for m in messages if m["role"] == "system"), "")
        chat_messages = [m for m in messages if m["role"] != "system"]
        
        params = {
            "messages": chat_messages,
            "system": system_message,  # System prompt goes in top-level parameter
            **self.config.params
        }

        if end_call_enabled:
            current_tools.append({
                "name": "end_call",
                "description": "Ends the conversation by deactivating the active call.",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            })
            
        if current_tools:
            params["tools"] = current_tools

        response = self.client.messages.create(**params)
        message_content = response.content[0].text

        end_call_detected = False
        for block in response.content:
            if block.type == "tool_use" and block.name == "end_call":
                end_call_detected = True
                break
        
        return message_content, end_call_detected
    
class TogetherAIProvider(OpenAIProvider):
    #The following models are supported:
    #meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
    #meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
    #meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo
    #meta-llama/Llama-3.3-70B-Instruct-Turbo
    #mistralai/Mixtral-8x7B-Instruct-v0.1
    #mistralai/Mistral-7B-Instruct-v0.1
    #Qwen/Qwen2.5-7B-Instruct-Turbo
    #Qwen/Qwen2.5-72B-Instruct-Turbo
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = OpenAI(
            base_url="https://api.together.xyz/v1",
            api_key=os.environ["TOGETHER_API_KEY"]
        )
    
class GroqProvider(OpenAIProvider):
    #The following models are supported:
    #qwen-2.5-32b
    #deepseek-r1-distill-qwen-32b
    #deepseek-r1-distill-llama-70b
    #llama-3.3-70b-versatile
    #llama-3.1-8b-instant
    #mixtral-8x7b-32768
    #gemma2-9b-it
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])

class DeepSeekProvider(OpenAIProvider):
    #The following models are supported:
    #deepseek-chat
    #deepseek-reasoner
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = OpenAI(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com"
        )

class CerebrasProvider(OpenAIProvider):
    #The following models are supported:
    #llama3.1-8b
    #llama-3.3-70b
    #DeepSeek-R1-Distill-Llama-70B
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = Cerebras(
            api_key=os.environ.get("CEREBRAS_API_KEY"),
        )

class XAIProvider(OpenAIProvider):
    #The following models are supported:
    #grok-2-latest
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = OpenAI(
            api_key=os.environ["XAI_API_KEY"],
            base_url="https://api.x.ai/v1"
        )
        
    def get_completion(
            self,
            messages: List[Dict],
            end_call_enabled: bool = True,
            tools: Optional[List[Dict]] = None
    ) -> tuple[str, Optional[Dict]]:
        current_tools = [] if tools is None else tools.copy()
        
        params = {
            "messages": messages,
            **self.config.params
        }
        
        if end_call_enabled:
            current_tools.append({
                "type": "function",
                "function": {
                    "name": "end_call",
                    "description": "Ends the conversation by deactivating the active call.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    },
                    "strict": False
                }
            })
            
        if current_tools:
            params["tools"] = current_tools
            params["tool_choice"] = "auto"
            
        response = self.client.chat.completions.create(**params)
        message_content = response.choices[0].message.content
        tool_calls = response.choices[0].message.tool_calls or []
        
        end_call_detected = False
        for tool_call in tool_calls:
            if tool_call.function.name == "end_call":
                end_call_detected = True
                break

        return message_content, end_call_detected

class GeminiProvider(LLMProvider):
    #The following model is supported:
    #gemini-2.0-flash
    #gemini-2.0-flash-lite-preview-02-05
    #gemini-1.5-flash
    #gemini-1.5-flash-8b
    #gemini-1.5-pro
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        
        # Convert the end_call method to an OpenAPI-style function declaration
        self.end_call_fn_decl = types.FunctionDeclaration.from_callable(
            callable=self.end_call, client=self.client
        )
        # Wrap the declaration in a Tool object
        self.end_call_tool = types.Tool(function_declarations=[self.end_call_fn_decl])
    
    def end_call(self) -> bool:
        """This function can be called by the LLM to end the conversation."""
        return True

    def get_completion(
        self,
        messages: List[Dict],
        end_call_enabled: bool = True,
        tools: Optional[List[types.Tool]] = None
    ) -> tuple[str, Optional[Dict]]:
        # Start with any additional tools provided
        current_tools = [] if tools is None else tools.copy()
        
        # Add the end_call tool if enabled
        if end_call_enabled:
            current_tools.append(self.end_call_tool)
        
        # Convert OpenAI-style messages to Gemini format
        history = []
        for msg in messages:
            # Map assistant messages to the model role, all others as user
            role = "model" if msg["role"] == "assistant" else "user"
            history.append(
                types.Content(
                    parts=[types.Part(text=msg["content"])],
                    role=role
                )
            )
        
        # Build a configuration dictionary that includes our tools.
        config = {'tools': current_tools}
        
        # Create a chat session with the chat history (all except the last message)
        chat = self.client.chats.create(
            history=history[:-1] if history else [],
            config=config,
            **self.config.params
        )
        
        # Send the latest message and get the response
        if history:
            response = chat.send_message(history[-1].parts[0].text)
        else:
            return "", False
        
        # Check if any function calls were returned from the model
        function_calls = response.function_calls or []
        #print("Function calls returned:", function_calls)
        
        # Detect if the model called the 'end_call' function
        end_call_detected = any(fn.name == "end_call" for fn in function_calls)
        if end_call_detected:
            #print("End call detected")
            return "", True
        return response.text, False
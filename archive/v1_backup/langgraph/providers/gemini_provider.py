"""
Google Gemini Provider
Implements the LLM interface for Google's Gemini AI models
"""

import os
import logging
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)

class GeminiProvider:
    """Google Gemini LLM Provider"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-pro",
        temperature: float = 0.1,
        max_tokens: int = 4000,
        top_p: float = 0.8,
        top_k: int = 10,
        **kwargs
    ):
        """
        Initialize Gemini provider
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            model: Gemini model name (gemini-pro, gemini-pro-vision)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum output tokens
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model_name = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.top_k = top_k
        
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        try:
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                    top_p=self.top_p,
                    top_k=self.top_k,
                ),
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }
            )
            logger.info(f"Initialized Gemini provider with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            raise
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text response from Gemini
        
        Args:
            prompt: User prompt
            system_prompt: System instruction (prepended to prompt)
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional parameters
        
        Returns:
            Generated text response
        """
        try:
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
            
            # Generate response
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature or self.temperature,
                    max_output_tokens=max_tokens or self.max_tokens,
                    top_p=self.top_p,
                    top_k=self.top_k,
                )
            )
            
            if response.candidates:
                return response.candidates[0].content.parts[0].text.strip()
            else:
                logger.warning("Gemini returned no candidates")
                return ""
                
        except Exception as e:
            logger.error(f"Gemini generation failed: {str(e)}")
            raise
    
    def generate_structured(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured response (JSON) from Gemini
        
        Args:
            prompt: User prompt
            response_schema: Expected JSON schema
            system_prompt: System instruction
            **kwargs: Additional parameters
        
        Returns:
            Parsed JSON response
        """
        import json
        
        # Create system prompt for structured response
        schema_prompt = f"""
        You must respond with valid JSON that matches this exact schema:
        {json.dumps(response_schema, indent=2)}
        
        Respond only with the JSON, no additional text or explanation.
        """
        
        if system_prompt:
            full_system_prompt = f"{system_prompt}\n\n{schema_prompt}"
        else:
            full_system_prompt = schema_prompt
        
        try:
            response_text = self.generate(
                prompt=prompt,
                system_prompt=full_system_prompt,
                **kwargs
            )
            
            # Try to parse JSON
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from Gemini: {str(e)}")
            logger.debug(f"Raw response: {response_text}")
            
            # Return error structure
            return {
                "error": "Failed to parse JSON response",
                "raw_response": response_text,
                "parse_error": str(e)
            }
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Multi-turn chat conversation
        
        Args:
            messages: List of {"role": "user/assistant", "content": "..."}
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional parameters
        
        Returns:
            Assistant's response
        """
        try:
            # Convert messages to Gemini format
            chat_history = []
            for message in messages[:-1]:  # All but the last message
                if message["role"] == "user":
                    chat_history.append({"role": "user", "parts": [message["content"]]})
                elif message["role"] == "assistant":
                    chat_history.append({"role": "model", "parts": [message["content"]]})
            
            # Start chat session with history
            chat = self.model.start_chat(history=chat_history)
            
            # Send the latest message
            last_message = messages[-1]["content"]
            response = chat.send_message(
                last_message,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature or self.temperature,
                    max_output_tokens=max_tokens or self.max_tokens,
                    top_p=self.top_p,
                    top_k=self.top_k,
                )
            )
            
            if response.candidates:
                return response.candidates[0].content.parts[0].text.strip()
            else:
                logger.warning("Gemini chat returned no candidates")
                return ""
                
        except Exception as e:
            logger.error(f"Gemini chat failed: {str(e)}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "provider": "gemini",
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k,
        }
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for token usage (rough estimates)
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        
        Returns:
            Estimated cost in USD
        """
        # Gemini Pro pricing (as of 2024, check current rates)
        # These are rough estimates - check Google AI pricing for accurate rates
        input_cost_per_1k = 0.0005  # $0.0005 per 1K input tokens
        output_cost_per_1k = 0.0015  # $0.0015 per 1K output tokens
        
        input_cost = (input_tokens / 1000) * input_cost_per_1k
        output_cost = (output_tokens / 1000) * output_cost_per_1k
        
        return input_cost + output_cost
    
    def __str__(self) -> str:
        return f"GeminiProvider(model={self.model_name}, temp={self.temperature})"

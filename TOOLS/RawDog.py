from typing import Dict, Any
from rich.console import Console
from rich.markdown import Markdown
import os
import tomli
from groq import Groq
import openai
import google.generativeai as genai

class TaskExecutor:
    """
    Manages an interactive chat session, handling user input and AI responses.
    """

    def __init__(self) -> None:
        """Initializes the conversational assistant with default settings."""
        self._console: Console = Console()
        self._config = self._load_config()

        # Session configuration
        self._selected_provider: str = "openai"
        self._selected_model: str = "gpt-3.5-turbo"
        self._conversation_enabled: bool = True
        self._max_tokens: int = 600
        self._temperature: float = 0.2
        self._top_p: float = 0.999
        self._timeout: int = 30

        # Initialize API clients
        self._initialize_clients()

    def _load_config(self) -> dict:
        """Load configuration from config.toml file."""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                 'backend', 'AI', 'perplexica', 'config.toml')
        try:
            with open(config_path, 'rb') as f:
                return tomli.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def _initialize_clients(self) -> None:
        """Initialize API clients for different providers."""
        try:
            # Initialize OpenAI
            if 'API_KEYS' in self._config and 'OPENAI' in self._config['API_KEYS']:
                openai.api_key = self._config['API_KEYS']['OPENAI']

            # Initialize Groq
            if 'API_KEYS' in self._config and 'GROQ' in self._config['API_KEYS']:
                self._groq_client = Groq(api_key=self._config['API_KEYS']['GROQ'])

            # Initialize Gemini
            if 'API_KEYS' in self._config and 'GEMINI' in self._config['API_KEYS']:
                genai.configure(api_key=self._config['API_KEYS']['GEMINI'])
                self._gemini_model = genai.GenerativeModel('gemini-pro')

        except Exception as e:
            print(f"Error initializing API clients: {e}")

    def process_query(self, query: str) -> None:
        """
        Processes a user query and gets a response from the selected AI provider.

        Args:
            query: The user's text input.

        Returns:
            None
        """
        try:
            if self._selected_provider == "openai":
                response = self._get_openai_response(query)
            elif self._selected_provider == "groq":
                response = self._get_groq_response(query)
            elif self._selected_provider == "gemini":
                response = self._get_gemini_response(query)
            else:
                response = "Selected provider not implemented"

            self._console.print(Markdown(f"LLM: {response}"))

        except Exception as e:
            self._console.print(Markdown(f"LLM: [red]Error: {e}[/red]"))

    def _get_openai_response(self, query: str) -> str:
        """Get response from OpenAI."""
        response = openai.ChatCompletion.create(
            model=self._selected_model,
            messages=[{"role": "user", "content": query}],
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            top_p=self._top_p
        )
        return response.choices[0].message.content

    def _get_groq_response(self, query: str) -> str:
        """Get response from Groq."""
        response = self._groq_client.chat.completions.create(
            messages=[{"role": "user", "content": query}],
            model="mixtral-8x7b-32768",
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            top_p=self._top_p
        )
        return response.choices[0].message.content

    def _get_gemini_response(self, query: str) -> str:
        """Get response from Gemini."""
        response = self._gemini_model.generate_content(query)
        return response.text

if __name__ == "__main__":
    assistant = TaskExecutor()
    while True:
        input_query = input("Enter your query: ")
        assistant.process_query(input_query)
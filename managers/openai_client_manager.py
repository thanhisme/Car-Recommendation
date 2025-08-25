import os
from openai import OpenAI

class OpenAIClientManager:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    def get_embedding(self, text: str, model: str = None) -> list:
        model_name = model or os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
        response = self.client.embeddings.create(model=model_name, input=text)
        return response.data[0].embedding

    def chat_completion(self, messages, model: str = None, **kwargs):
        """
        Create a chat completion using the new OpenAI API
        """
        print(messages)
        model_name = model or os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo")
        return self.client.chat.completions.create(model=model_name, messages=messages, **kwargs)

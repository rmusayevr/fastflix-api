import os
from anthropic import Anthropic
from sentence_transformers import SentenceTransformer


class AIService:
    _model = None
    _anthropic_client = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = SentenceTransformer("all-MiniLM-L6-v2")
        return cls._model

    @classmethod
    def get_anthropic_client(cls):
        if cls._anthropic_client is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                cls._anthropic_client = Anthropic(api_key=api_key)
        return cls._anthropic_client

    @classmethod
    def generate_embedding(cls, text: str) -> list[float]:
        if not text:
            return [0.0] * 384
        model = cls.get_model()
        return model.encode(text).tolist()

    @classmethod
    def generate_answer(cls, context: str, question: str) -> str:
        """
        Uses Claude to answer the question based strictly on the context.
        """
        client = cls.get_anthropic_client()

        if not client:
            return f"🤖 [Mock Claude]: Based on my database, I found this: {context}"

        try:
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                system="""
                You are a helpful movie assistant. Answer the user's question using ONLY the 
                context provided below. If the answer isn't in the context, say 'I don't know'.
                """,
                messages=[
                    {
                        "role": "user",
                        "content": f"Context: {context}\n\nQuestion: {question}",
                    }
                ],
            )
            return response.content[0].text

        except Exception as e:
            return f"⚠️ AI Error: {str(e)}"


def get_embedding(text: str):
    return AIService.generate_embedding(text)

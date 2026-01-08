from sentence_transformers import SentenceTransformer


class AIService:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            print("🤖 Loading AI Model (all-MiniLM-L6-v2)...")
            cls._model = SentenceTransformer("all-MiniLM-L6-v2")
        return cls._model

    @classmethod
    def generate_embedding(cls, text: str) -> list[float]:
        """
        Converts text into a 384-dimensional vector.
        """
        if not text:
            return [0.0] * 384

        model = cls.get_model()
        vector = model.encode(text).tolist()
        return vector


def get_embedding(text: str):
    return AIService.generate_embedding(text)

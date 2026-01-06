import meilisearch
from app.core.config import settings


class SearchClient:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            try:
                cls._client = meilisearch.Client(
                    settings.MEILI_HOST, settings.MEILI_MASTER_KEY
                )
            except Exception as e:
                print(f"⚠️ Search Engine Connection Failed: {e}")
                return None
        return cls._client

    @classmethod
    def check_health(cls):
        """Returns True if MeiliSearch is responsive"""
        client = cls.get_client()
        if client:
            try:
                return client.health().get("status") == "available"
            except:
                return False
        return False


def get_search_client():
    return SearchClient.get_client()

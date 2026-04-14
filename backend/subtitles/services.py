import requests
from django.conf import settings


class OllamaTranslationService:
    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL

    def translate_text(self, text: str) -> str:
        prompt = f"Translate the following subtitle text from English to Swahili. Only return the translation:\n{text}"
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={'model': self.model, 'prompt': prompt, 'stream': False},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data.get('response', '').strip()

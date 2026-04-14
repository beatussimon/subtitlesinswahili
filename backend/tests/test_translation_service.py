from unittest.mock import patch

from subtitles.services import OllamaTranslationService


@patch('subtitles.services.requests.post')
def test_translation_service_posts_expected_payload(mock_post):
    mock_post.return_value.json.return_value = {'response': 'Habari'}
    mock_post.return_value.raise_for_status.return_value = None

    service = OllamaTranslationService(base_url='http://ollama:11434', model='llama3.1')
    translated = service.translate_text('Hello')

    assert translated == 'Habari'
    args, kwargs = mock_post.call_args
    assert args[0] == 'http://ollama:11434/api/generate'
    assert kwargs['json']['model'] == 'llama3.1'
    assert 'Hello' in kwargs['json']['prompt']

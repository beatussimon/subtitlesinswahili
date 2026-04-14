from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from subtitles.models import TranslationJob


SRT_SAMPLE = b"""1
00:00:01,000 --> 00:00:02,500
Hello world
"""


def test_upload_endpoint_works(db):
    client = Client()

    with patch('subtitles.views.translate_subtitle_task.delay') as mocked_delay:
        response = client.post(
            '/api/upload/',
            {'file': SimpleUploadedFile('sample.srt', SRT_SAMPLE, content_type='application/x-subrip')},
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload['status'] == 'pending'
    mocked_delay.assert_called_once()


def test_status_endpoint_works(db):
    job = TranslationJob.objects.create(
        original_filename='sample.srt',
        original_content=SRT_SAMPLE.decode('utf-8'),
        status=TranslationJob.STATUS_PROCESSING,
    )
    client = Client()

    response = client.get(f'/api/status/{job.id}/')

    assert response.status_code == 200
    assert response.json()['status'] == TranslationJob.STATUS_PROCESSING


def test_download_endpoint_works(db):
    job = TranslationJob.objects.create(
        original_filename='sample.srt',
        original_content=SRT_SAMPLE.decode('utf-8'),
        translated_content='1\n00:00:01,000 --> 00:00:02,500\nHabari dunia\n',
        status=TranslationJob.STATUS_COMPLETED,
    )
    client = Client()

    response = client.get(f'/api/download/{job.id}/')

    assert response.status_code == 200
    assert 'Habari dunia' in response.content.decode('utf-8')

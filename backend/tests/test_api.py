import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from subtitles.models import Subtitle, TranslationJob


SRT_SAMPLE = b"""1
00:00:01,000 --> 00:00:02,500
Hello world
"""


def test_seeded_subtitles_visible(db):
    client = Client()
    response = client.get('/api/subtitles/')

    assert response.status_code == 200
    assert len(response.json()['subtitles']) >= 3


def test_register_login_and_download_requires_auth(db):
    subtitle = Subtitle.objects.first()
    client = Client()

    unauth_response = client.get(f'/api/subtitles/{subtitle.id}/download/')
    assert unauth_response.status_code == 401

    register_response = client.post(
        '/api/auth/register/',
        data=json.dumps({'username': 'juma', 'password': 'password123'}),
        content_type='application/json',
    )
    assert register_response.status_code == 201

    auth_response = client.get(f'/api/subtitles/{subtitle.id}/download/')
    assert auth_response.status_code == 200


def test_upload_endpoint_requires_auth_and_works(db):
    client = Client()

    unauth = client.post(
        '/api/upload/',
        {'file': SimpleUploadedFile('sample.srt', SRT_SAMPLE, content_type='application/x-subrip')},
    )
    assert unauth.status_code == 401

    User.objects.create_user(username='tester', password='password123')
    client.login(username='tester', password='password123')

    with patch('subtitles.views.translate_subtitle_task.delay') as mocked_delay:
        response = client.post(
            '/api/upload/',
            {'file': SimpleUploadedFile('sample.srt', SRT_SAMPLE, content_type='application/x-subrip')},
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload['status'] == 'pending'
    assert payload['translation_fee_tsh'] == 1000
    mocked_delay.assert_called_once()


def test_comment_and_request_endpoints(db):
    subtitle = Subtitle.objects.first()
    User.objects.create_user(username='tester2', password='password123')
    client = Client()
    client.login(username='tester2', password='password123')

    comment_response = client.post(
        f'/api/subtitles/{subtitle.id}/comments/create/',
        data=json.dumps({'body': 'Hii subtitle ni safi sana!'}),
        content_type='application/json',
    )
    assert comment_response.status_code == 201

    request_response = client.post(
        '/api/requests/create/',
        data=json.dumps({'requested_title': 'Inception', 'requested_year': 2010}),
        content_type='application/json',
    )
    assert request_response.status_code == 201


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


def test_download_endpoint_works_for_authenticated_users(db):
    User.objects.create_user(username='dl', password='password123')
    job = TranslationJob.objects.create(
        original_filename='sample.srt',
        original_content=SRT_SAMPLE.decode('utf-8'),
        translated_content='1\n00:00:01,000 --> 00:00:02,500\nHabari dunia\n',
        status=TranslationJob.STATUS_COMPLETED,
    )
    client = Client()

    anon_response = client.get(f'/api/download/{job.id}/')
    assert anon_response.status_code == 401

    client.login(username='dl', password='password123')
    response = client.get(f'/api/download/{job.id}/')

    assert response.status_code == 200
    assert 'Habari dunia' in response.content.decode('utf-8')

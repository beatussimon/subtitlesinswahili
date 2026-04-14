import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from subtitles.models import Bookmark, Category, Subtitle, SubtitleComment, SubtitleRequest, TranslationJob
from subtitles.srt_utils import parse_srt
from subtitles.tasks import translate_subtitle_task



def _json_body(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return {}


@csrf_exempt
@require_http_methods(['POST'])
def register_user(request):
    data = _json_body(request)
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return JsonResponse({'error': 'username and password are required'}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'username already exists'}, status=400)

    user = User.objects.create_user(username=username, password=password)
    login(request, user)
    return JsonResponse({'id': user.id, 'username': user.username}, status=201)


@csrf_exempt
@require_http_methods(['POST'])
def login_user(request):
    data = _json_body(request)
    user = authenticate(request, username=data.get('username', '').strip(), password=data.get('password', ''))
    if not user:
        return JsonResponse({'error': 'invalid credentials'}, status=401)

    login(request, user)
    return JsonResponse({'id': user.id, 'username': user.username})


@csrf_exempt
@require_http_methods(['POST'])
def logout_user(request):
    logout(request)
    return JsonResponse({'ok': True})


@require_http_methods(['GET'])
def current_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False})

    return JsonResponse({'authenticated': True, 'id': request.user.id, 'username': request.user.username})


@require_http_methods(['GET'])
def list_categories(request):
    categories = list(Category.objects.values('id', 'name', 'slug'))
    return JsonResponse({'categories': categories})


@require_http_methods(['GET'])
def list_subtitles(request):
    category_slug = request.GET.get('category')
    subtitles = Subtitle.objects.select_related('category').all()
    if category_slug:
        subtitles = subtitles.filter(category__slug=category_slug)

    payload = [
        {
            'id': subtitle.id,
            'title': subtitle.title,
            'movie_year': subtitle.movie_year,
            'synopsis': subtitle.synopsis,
            'language': subtitle.language,
            'category': subtitle.category.name,
            'category_slug': subtitle.category.slug,
            'translation_fee_tsh': subtitle.translation_fee_tsh,
            'comments_count': subtitle.comments.count(),
            'bookmarks_count': subtitle.bookmarks.count(),
        }
        for subtitle in subtitles
    ]
    return JsonResponse({'subtitles': payload})


@csrf_exempt
@require_http_methods(['POST'])
def upload_subtitle(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'authentication required'}, status=401)

    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return JsonResponse({'error': 'No file provided'}, status=400)

    if not uploaded_file.name.endswith('.srt'):
        return JsonResponse({'error': 'Only .srt files are allowed'}, status=400)

    content = uploaded_file.read().decode('utf-8')

    try:
        parse_srt(content)
    except Exception as exc:
        return JsonResponse({'error': f'Invalid SRT file: {exc}'}, status=400)

    job = TranslationJob.objects.create(
        original_filename=uploaded_file.name,
        original_content=content,
        status=TranslationJob.STATUS_PENDING,
    )
    translate_subtitle_task.delay(job.id)

    return JsonResponse({'job_id': job.id, 'status': job.status, 'translation_fee_tsh': 1000}, status=201)


@require_http_methods(['GET'])
def translation_status(request, job_id: int):
    try:
        job = TranslationJob.objects.get(id=job_id)
    except TranslationJob.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)

    return JsonResponse(
        {
            'job_id': job.id,
            'status': job.status,
            'error_message': job.error_message,
            'subtitle_id': job.translated_subtitle_id,
        }
    )


@require_http_methods(['GET'])
def download_translation(request, job_id: int):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'authentication required before download'}, status=401)

    try:
        job = TranslationJob.objects.get(id=job_id)
    except TranslationJob.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)

    if job.status != TranslationJob.STATUS_COMPLETED or not job.translated_content:
        return JsonResponse({'error': 'Translation not ready'}, status=400)

    response = HttpResponse(job.translated_content, content_type='application/x-subrip')
    response['Content-Disposition'] = f'attachment; filename="{job.original_filename}"'
    return response


@require_http_methods(['GET'])
def download_subtitle(request, subtitle_id: int):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'authentication required before download'}, status=401)

    subtitle = Subtitle.objects.filter(id=subtitle_id).first()
    if not subtitle:
        return JsonResponse({'error': 'Subtitle not found'}, status=404)

    response = HttpResponse(subtitle.srt_content, content_type='application/x-subrip')
    response['Content-Disposition'] = f'attachment; filename="{subtitle.title}.srt"'
    return response


@csrf_exempt
@require_http_methods(['POST'])
def toggle_bookmark(request, subtitle_id: int):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'authentication required'}, status=401)

    subtitle = Subtitle.objects.filter(id=subtitle_id).first()
    if not subtitle:
        return JsonResponse({'error': 'Subtitle not found'}, status=404)

    bookmark = Bookmark.objects.filter(user=request.user, subtitle=subtitle).first()
    if bookmark:
        bookmark.delete()
        return JsonResponse({'bookmarked': False})

    Bookmark.objects.create(user=request.user, subtitle=subtitle)
    return JsonResponse({'bookmarked': True})


@csrf_exempt
@require_http_methods(['POST'])
def create_comment(request, subtitle_id: int):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'authentication required'}, status=401)

    subtitle = Subtitle.objects.filter(id=subtitle_id).first()
    if not subtitle:
        return JsonResponse({'error': 'Subtitle not found'}, status=404)

    data = _json_body(request)
    body = data.get('body', '').strip()
    if not body:
        return JsonResponse({'error': 'comment body is required'}, status=400)

    comment = SubtitleComment.objects.create(user=request.user, subtitle=subtitle, body=body)
    return JsonResponse({'id': comment.id, 'body': comment.body, 'username': request.user.username}, status=201)


@require_http_methods(['GET'])
def list_comments(request, subtitle_id: int):
    subtitle = Subtitle.objects.filter(id=subtitle_id).first()
    if not subtitle:
        return JsonResponse({'error': 'Subtitle not found'}, status=404)

    comments = [
        {'id': c.id, 'body': c.body, 'username': c.user.username, 'created_at': c.created_at.isoformat()}
        for c in subtitle.comments.select_related('user').all()
    ]
    return JsonResponse({'comments': comments})


@csrf_exempt
@require_http_methods(['POST'])
def create_subtitle_request(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'authentication required'}, status=401)

    data = _json_body(request)
    requested_title = data.get('requested_title', '').strip()
    if not requested_title:
        return JsonResponse({'error': 'requested_title is required'}, status=400)

    subtitle_request = SubtitleRequest.objects.create(
        requested_title=requested_title,
        requested_year=data.get('requested_year') or None,
        notes=data.get('notes', '').strip(),
        requested_by=request.user,
    )
    return JsonResponse({'id': subtitle_request.id, 'status': subtitle_request.status}, status=201)


@require_http_methods(['GET'])
def list_subtitle_requests(request):
    requests = [
        {
            'id': item.id,
            'requested_title': item.requested_title,
            'requested_year': item.requested_year,
            'notes': item.notes,
            'status': item.status,
            'requested_by': item.requested_by.username,
        }
        for item in SubtitleRequest.objects.select_related('requested_by').all()
    ]
    return JsonResponse({'requests': requests})

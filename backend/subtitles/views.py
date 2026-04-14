from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from subtitles.models import TranslationJob
from subtitles.srt_utils import parse_srt
from subtitles.tasks import translate_subtitle_task


@csrf_exempt
def upload_subtitle(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

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

    return JsonResponse({'job_id': job.id, 'status': job.status}, status=201)


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
        }
    )


def download_translation(request, job_id: int):
    try:
        job = TranslationJob.objects.get(id=job_id)
    except TranslationJob.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)

    if job.status != TranslationJob.STATUS_COMPLETED or not job.translated_content:
        return JsonResponse({'error': 'Translation not ready'}, status=400)

    response = HttpResponse(job.translated_content, content_type='application/x-subrip')
    response['Content-Disposition'] = f'attachment; filename="{job.original_filename}"'
    return response

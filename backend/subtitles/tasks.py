from celery import shared_task

from subtitles.models import TranslationJob
from subtitles.services import OllamaTranslationService
from subtitles.srt_utils import parse_srt, serialize_srt, SubtitleEntry


@shared_task
def translate_subtitle_task(job_id: int):
    job = TranslationJob.objects.get(id=job_id)
    job.status = TranslationJob.STATUS_PROCESSING
    job.save(update_fields=['status', 'updated_at'])

    try:
        entries = parse_srt(job.original_content)
        service = OllamaTranslationService()

        translated_entries = []
        for entry in entries:
            translated_text = service.translate_text(entry.text)
            translated_entries.append(
                SubtitleEntry(index=entry.index, timestamp=entry.timestamp, text=translated_text)
            )

        job.translated_content = serialize_srt(translated_entries)
        job.status = TranslationJob.STATUS_COMPLETED
        job.error_message = ''
        job.save(update_fields=['translated_content', 'status', 'error_message', 'updated_at'])
    except Exception as exc:
        job.status = TranslationJob.STATUS_FAILED
        job.error_message = str(exc)
        job.save(update_fields=['status', 'error_message', 'updated_at'])
        raise

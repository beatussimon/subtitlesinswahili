from celery import shared_task
from django.utils.text import slugify

from subtitles.models import Category, Subtitle, TranslationJob
from subtitles.services import OllamaTranslationService
from subtitles.srt_utils import SubtitleEntry, parse_srt, serialize_srt


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

        translated_content = serialize_srt(translated_entries)
        category, _ = Category.objects.get_or_create(name='Translated', defaults={'slug': slugify('Translated')})
        subtitle = Subtitle.objects.create(
            title=job.original_filename.replace('.srt', ''),
            movie_year=2026,
            synopsis='Translated from upload.',
            srt_content=translated_content,
            source='translation',
            translated_from='English',
            translation_fee_tsh=1000,
            category=category,
        )

        job.translated_content = translated_content
        job.translated_subtitle = subtitle
        job.status = TranslationJob.STATUS_COMPLETED
        job.error_message = ''
        job.save(update_fields=['translated_content', 'translated_subtitle', 'status', 'error_message', 'updated_at'])
    except Exception as exc:
        job.status = TranslationJob.STATUS_FAILED
        job.error_message = str(exc)
        job.save(update_fields=['status', 'error_message', 'updated_at'])
        raise

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def seed_initial_data(apps, schema_editor):
    Category = apps.get_model('subtitles', 'Category')
    Subtitle = apps.get_model('subtitles', 'Subtitle')

    action = Category.objects.create(name='Action', slug='action')
    drama = Category.objects.create(name='Drama', slug='drama')
    comedy = Category.objects.create(name='Comedy', slug='comedy')

    samples = [
        {
            'title': 'Fast Horizon',
            'movie_year': 2023,
            'category': action,
            'synopsis': 'A getaway driver races to expose a city-wide conspiracy.',
            'srt_content': '1\n00:00:01,000 --> 00:00:03,000\nTwende haraka!\n',
        },
        {
            'title': 'Usiku wa Ahadi',
            'movie_year': 2021,
            'category': drama,
            'synopsis': 'Two siblings reunite to protect their family legacy.',
            'srt_content': '1\n00:00:01,000 --> 00:00:03,000\nNitarudi kabla ya alfajiri.\n',
        },
        {
            'title': 'Mtaa wa Kicheko',
            'movie_year': 2024,
            'category': comedy,
            'synopsis': 'Three friends run a prank show in Dar es Salaam.',
            'srt_content': '1\n00:00:01,000 --> 00:00:03,000\nHii ni balaa kabisa!\n',
        },
    ]

    for sample in samples:
        Subtitle.objects.create(
            title=sample['title'],
            movie_year=sample['movie_year'],
            category=sample['category'],
            synopsis=sample['synopsis'],
            srt_content=sample['srt_content'],
            source='seed',
            translated_from='English',
            translation_fee_tsh=1000,
        )


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subtitles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=120, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subtitle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('movie_year', models.PositiveIntegerField()),
                ('language', models.CharField(default='Swahili', max_length=60)),
                ('synopsis', models.TextField(blank=True)),
                ('srt_content', models.TextField()),
                ('source', models.CharField(default='upload', max_length=40)),
                ('translated_from', models.CharField(blank=True, max_length=60)),
                ('translation_fee_tsh', models.PositiveIntegerField(default=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'category',
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subtitles', to='subtitles.category'),
                ),
                (
                    'created_by',
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='SubtitleRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_title', models.CharField(max_length=255)),
                ('requested_year', models.PositiveIntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                (
                    'status',
                    models.CharField(
                        choices=[('open', 'Open'), ('in_progress', 'In Progress'), ('done', 'Done')],
                        default='open',
                        max_length=20,
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'requested_by',
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subtitle_requests', to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='SubtitleComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('subtitle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='subtitles.subtitle')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('subtitle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarks', to='subtitles.subtitle')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookmarks', to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('user', 'subtitle')}},
        ),
        migrations.AddField(
            model_name='translationjob',
            name='translated_subtitle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='subtitles.subtitle'),
        ),
        migrations.RunPython(seed_initial_data, migrations.RunPython.noop),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='TranslationJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_filename', models.CharField(max_length=255)),
                ('original_content', models.TextField()),
                ('translated_content', models.TextField(blank=True)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('pending', 'Pending'),
                            ('processing', 'Processing'),
                            ('completed', 'Completed'),
                            ('failed', 'Failed'),
                        ],
                        default='pending',
                        max_length=20,
                    ),
                ),
                ('error_message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]

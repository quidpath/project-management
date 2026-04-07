# Generated migration for adding draft status to Task

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0XXX_previous_migration'),  # Update with actual previous migration
    ]

    operations = [
        # Add 'draft' status to Task STATUS_CHOICES
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('draft', 'Draft'),
                    ('backlog', 'Backlog'),
                    ('todo', 'To Do'),
                    ('in_progress', 'In Progress'),
                    ('in_review', 'In Review'),
                    ('done', 'Done'),
                ],
                default='draft'
            ),
        ),
        migrations.AddField(
            model_name='task',
            name='drafted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='posted_at',
            field=models.DateTimeField(blank=True, null=True, help_text='When task was assigned to sprint'),
        ),
        migrations.AddField(
            model_name='task',
            name='posted_by',
            field=models.UUIDField(blank=True, null=True, help_text='User ID who posted the task'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['status'], name='task_status_idx'),
        ),
    ]

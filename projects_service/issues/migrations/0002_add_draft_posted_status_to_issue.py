# Generated migration for adding draft status to Issue

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0001_initial'),
    ]

    operations = [
        # Add 'draft' status to Issue STATUS_CHOICES
        migrations.AlterField(
            model_name='issue',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('draft', 'Draft'),
                    ('open', 'Open'),
                    ('in_progress', 'In Progress'),
                    ('resolved', 'Resolved'),
                    ('closed', 'Closed'),
                    ('wont_fix', "Won't Fix"),
                ],
                default='draft'
            ),
        ),
        migrations.AddField(
            model_name='issue',
            name='drafted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='issue',
            name='posted_at',
            field=models.DateTimeField(blank=True, null=True, help_text='When issue was opened/published'),
        ),
        migrations.AddField(
            model_name='issue',
            name='posted_by',
            field=models.UUIDField(blank=True, null=True, help_text='User ID who posted the issue'),
        ),
        migrations.AddIndex(
            model_name='issue',
            index=models.Index(fields=['status'], name='issue_status_idx'),
        ),
    ]

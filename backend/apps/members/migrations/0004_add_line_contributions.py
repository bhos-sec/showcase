# Generated migration for adding line contribution tracking

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0003_seed_badges"),
    ]

    operations = [
        migrations.AddField(
            model_name="member",
            name="additions",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Total lines added across all contributions (cached).",
            ),
        ),
        migrations.AddField(
            model_name="member",
            name="deletions",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Total lines deleted across all contributions (cached).",
            ),
        ),
        migrations.AddField(
            model_name="contribution",
            name="additions",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Lines of code added in this contribution.",
            ),
        ),
        migrations.AddField(
            model_name="contribution",
            name="deletions",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Lines of code deleted in this contribution.",
            ),
        ),
    ]

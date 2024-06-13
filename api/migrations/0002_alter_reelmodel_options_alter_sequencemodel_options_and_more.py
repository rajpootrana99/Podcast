# Generated by Django 5.0.6 on 2024-06-09 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reelmodel',
            options={'ordering': ['reel_number']},
        ),
        migrations.AlterModelOptions(
            name='sequencemodel',
            options={'ordering': ['sequence_number']},
        ),
        migrations.RemoveField(
            model_name='chaptermodel',
            name='user',
        ),
        migrations.RemoveField(
            model_name='episodemodel',
            name='user',
        ),
        migrations.AlterUniqueTogether(
            name='reelmodel',
            unique_together={('episode', 'reel_number')},
        ),
        migrations.RemoveField(
            model_name='sequencemodel',
            name='user',
        ),
        migrations.RemoveField(
            model_name='reelmodel',
            name='chapter',
        ),
        migrations.RemoveField(
            model_name='reelmodel',
            name='user',
        ),
    ]
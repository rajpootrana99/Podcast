# Generated by Django 5.0.6 on 2024-06-16 11:42

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='EpisodeModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField(blank=True, null=True)),
                ('start_time', models.CharField(max_length=12, null=True)),
                ('end_time', models.CharField(max_length=12, null=True)),
                ('sheet_link', models.URLField()),
                ('project_link', models.URLField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserModel',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('full_name', models.CharField(max_length=255)),
                ('profile_image', models.ImageField(default=None, null=True, upload_to='uploads/user')),
                ('is_active', models.BooleanField(default=True)),
                ('is_third_party', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SequenceModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('words', models.CharField(max_length=255)),
                ('sequence_number', models.PositiveBigIntegerField()),
                ('start_time', models.CharField(max_length=12)),
                ('end_time', models.CharField(max_length=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sequences', to='api.episodemodel')),
            ],
            options={
                'ordering': ['sequence_number'],
            },
        ),
        migrations.CreateModel(
            name='ChapterModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('chapter_number', models.PositiveBigIntegerField()),
                ('content', models.TextField(blank=True, null=True)),
                ('start_time', models.CharField(max_length=12, null=True)),
                ('end_time', models.CharField(max_length=12, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chapters', to='api.episodemodel')),
                ('sequences', models.ManyToManyField(related_name='chapters', to='api.sequencemodel')),
            ],
            options={
                'ordering': ['chapter_number'],
                'unique_together': {('episode', 'chapter_number')},
            },
        ),
        migrations.CreateModel(
            name='ReelModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('reel_number', models.PositiveBigIntegerField()),
                ('content', models.TextField(blank=True, null=True)),
                ('start_time', models.CharField(max_length=12, null=True)),
                ('end_time', models.CharField(max_length=12, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('chapter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reels', to='api.chaptermodel')),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reels', to='api.episodemodel')),
                ('sequences', models.ManyToManyField(related_name='reels', to='api.sequencemodel')),
            ],
            options={
                'ordering': ['reel_number'],
                'unique_together': {('chapter', 'reel_number')},
            },
        ),
    ]

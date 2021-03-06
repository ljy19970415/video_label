# Generated by Django 2.0 on 2020-04-29 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videoLabel', '0002_auto_20200429_1503'),
    ]

    operations = [
        migrations.CreateModel(
            name='user_videoDB',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('video_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='videoDB',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('video_name', models.CharField(max_length=25)),
                ('action_label', models.BooleanField(default=False)),
                ('object_label', models.BooleanField(default=False)),
                ('fps', models.FloatField()),
                ('frame_num', models.IntegerField()),
            ],
        ),
        migrations.RenameModel(
            old_name='user',
            new_name='userDB',
        ),
    ]

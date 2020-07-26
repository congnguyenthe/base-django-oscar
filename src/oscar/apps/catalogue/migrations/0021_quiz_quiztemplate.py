# Generated by Django 2.2.12 on 2020-07-10 15:46

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0020_auto_20200710_1447'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuizTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True, verbose_name='Name')),
                ('top_left', models.TextField(blank=True, null=True, verbose_name='Top Left')),
                ('top_right', models.TextField(blank=True, null=True, verbose_name='Top Right')),
                ('title', models.TextField(blank=True, null=True, verbose_name='Title')),
                ('bottom_left', models.TextField(blank=True, null=True, verbose_name='Name')),
                ('bottom_right', models.TextField(blank=True, null=True, verbose_name='Name')),
                ('page_num', models.BooleanField(default=True, help_text='Show page number in the document', verbose_name='Show Page Num')),
            ],
            options={
                'verbose_name': 'Quiz Template',
                'verbose_name_plural': 'Quiz Templates',
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True, verbose_name='Name')),
                ('item_list', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None)),
                ('product_class', models.OneToOneField(blank=True, help_text='Choose what type of quiz this is', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='quiz', to='catalogue.ProductClass', verbose_name='Quiz type')),
            ],
            options={
                'verbose_name': 'Quiz',
                'verbose_name_plural': 'Quizzes',
                'ordering': ['name'],
                'abstract': False,
            },
        ),
    ]
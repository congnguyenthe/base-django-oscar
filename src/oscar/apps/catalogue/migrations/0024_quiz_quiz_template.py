# Generated by Django 2.2.12 on 2020-07-11 03:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0023_auto_20200711_0254'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='quiz_template',
            field=models.ForeignKey(blank=True, help_text='Choose what template of quiz this is', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='quiz_template', to='catalogue.QuizTemplate', verbose_name='Quiz type'),
        ),
    ]

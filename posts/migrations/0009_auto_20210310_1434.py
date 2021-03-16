# Generated by Django 2.2.6 on 2021-03-10 11:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20210310_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(help_text='У группы должно быть описание', verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(blank=True, help_text='Выберите имя автора', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Выберите название группы', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='posts', to='posts.Group', verbose_name='Группа'),
        ),
    ]

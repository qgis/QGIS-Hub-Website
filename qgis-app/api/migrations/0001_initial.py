# Generated by Django 4.2.16 on 2024-11-18 03:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('token_blacklist', '0012_alter_outstandingtoken_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserOutstandingToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_blacklisted', models.BooleanField(default=False)),
                ('is_newly_created', models.BooleanField(default=False)),
                ('description', models.CharField(blank=True, help_text="Describe this token so that it's easier to remember where you're using it.", max_length=512, null=True, verbose_name='Description')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('last_used_at', models.DateTimeField(blank=True, null=True, verbose_name='Last used at')),
                ('token', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='token_blacklist.outstandingtoken')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

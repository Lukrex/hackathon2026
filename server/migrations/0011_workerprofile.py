from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0010_requestchatmessage_adminchatmessage'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categories', models.ManyToManyField(blank=True, related_name='workers', to='server.category')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='worker_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

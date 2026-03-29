from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0015_requestchatmessage_attachment_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestChatReadState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_read_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_read_states', to='server.request')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_chat_read_states', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'request')},
            },
        ),
    ]

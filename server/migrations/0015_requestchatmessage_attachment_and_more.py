from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0014_adminchatmessage_attachment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestchatmessage',
            name='message',
            field=models.TextField(blank=True, default='', max_length=4000),
        ),
        migrations.AddField(
            model_name='requestchatmessage',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='chat_uploads/%Y/%m/%d/'),
        ),
        migrations.AddField(
            model_name='requestchatmessage',
            name='attachment_type',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
    ]

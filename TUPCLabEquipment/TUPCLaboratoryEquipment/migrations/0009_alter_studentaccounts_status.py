# Generated by Django 5.1.1 on 2024-11-18 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TUPCLaboratoryEquipment', '0008_rename_verification_studentaccounts_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentaccounts',
            name='status',
            field=models.CharField(default='Deactivated', max_length=50),
        ),
    ]

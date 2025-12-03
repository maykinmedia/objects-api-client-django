from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "objectsapiclient",
            "0002_auto_20230917_1644",
        ),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Configuration",
            new_name="ObjectsClientConfiguration",
        ),
        migrations.RenameField(
            model_name="objectsclientconfiguration",
            old_name="objects_api_service",
            new_name="objects_api_service_config",
        ),
        migrations.RenameField(
            model_name="objectsclientconfiguration",
            old_name="object_type_api_service",
            new_name="object_type_api_service_config",
        ),
    ]

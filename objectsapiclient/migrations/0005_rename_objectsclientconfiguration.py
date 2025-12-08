# Generated manually for model and field renames

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("objectsapiclient", "0004_alter_objectsclientconfiguration_options_and_more"),
        ("zgw_consumers", "0016_auto_20220818_1412"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ObjectsClientConfiguration",
            new_name="ObjectsAPIServiceConfiguration",
        ),
        migrations.AlterModelOptions(
            name="objectsapiserviceconfiguration",
            options={"verbose_name": "Objects API service configuration"},
        ),
        migrations.RenameField(
            model_name="objectsapiserviceconfiguration",
            old_name="objects_api_service_config",
            new_name="objects_api_client_config",
        ),
        migrations.RenameField(
            model_name="objectsapiserviceconfiguration",
            old_name="object_type_api_service_config",
            new_name="objecttypes_api_client_config",
        ),
        migrations.AlterField(
            model_name="objectsapiserviceconfiguration",
            name="objects_api_client_config",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="objects_api_client_config",
                to="zgw_consumers.service",
            ),
        ),
        migrations.AlterField(
            model_name="objectsapiserviceconfiguration",
            name="objecttypes_api_client_config",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="objecttypes_api_client_config",
                to="zgw_consumers.service",
            ),
        ),
    ]

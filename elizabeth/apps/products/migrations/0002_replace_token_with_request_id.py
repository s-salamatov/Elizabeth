from __future__ import annotations

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="productdetailsrequest",
            name="request_id",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name="productdetailsrequest",
            name="token",
        ),
    ]

# Generated by Django 4.2.6 on 2023-10-30 05:21

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logistics", "0004_bill_organization_expense_organization_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="bill",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="billitem",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="record",
            name="record_type",
            field=models.IntegerField(
                choices=[(1, "Import"), (2, "Export")], default=1
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="stock",
            name="weight",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0"),
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
    ]

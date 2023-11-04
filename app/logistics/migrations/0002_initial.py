# Generated by Django 4.2.6 on 2023-10-20 12:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("fish", "0002_initial"),
        ("organizations", "0001_initial"),
        ("logistics", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="record",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="records",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="record",
            name="weigh_place",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="records",
                to="organizations.place",
            ),
        ),
        migrations.AddField(
            model_name="expense",
            name="type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="expenses",
                to="organizations.expensetype",
            ),
        ),
        migrations.AddField(
            model_name="expense",
            name="user",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"designation": 3},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="expenses",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="billitem",
            name="bill",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bill_items",
                to="logistics.bill",
            ),
        ),
        migrations.AddField(
            model_name="billitem",
            name="fish_variant",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bill_items",
                to="fish.fishvariant",
            ),
        ),
        migrations.AddField(
            model_name="bill",
            name="bill_place",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"type": 3},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bills",
                to="organizations.place",
            ),
        ),
        migrations.AddField(
            model_name="bill",
            name="discount",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bills",
                to="fish.discount",
            ),
        ),
        migrations.AddField(
            model_name="bill",
            name="user",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"designation": 3},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bills",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]

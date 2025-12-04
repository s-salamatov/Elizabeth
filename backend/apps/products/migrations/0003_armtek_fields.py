# Generated manually to add extended Armtek search attributes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "products",
            "0002_rename_products_p_pin_ab1b65_idx_products_pr_pin_a9174b_idx_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="available_quantity",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="currency",
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="delivery_date",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="import_flag",
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="importer_markup",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="is_analog",
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="markup",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="markup_rest_percent",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="markup_rest_rub",
            field=models.DecimalField(
                blank=True, decimal_places=4, max_digits=18, null=True
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="max_retail_price",
            field=models.DecimalField(
                blank=True, decimal_places=4, max_digits=18, null=True
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="minimum_order",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="multiplicity",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="note",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="price",
            field=models.DecimalField(
                blank=True, decimal_places=4, max_digits=18, null=True
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="producer_price",
            field=models.DecimalField(
                blank=True, decimal_places=4, max_digits=18, null=True
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="return_days",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="special_flag",
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="supply_probability",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=6, null=True
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="warehouse_code",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="warehouse_partner",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="warranty_date",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]

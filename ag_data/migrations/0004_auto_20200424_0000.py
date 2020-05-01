# Generated by Django 2.2.11 on 2020-04-24 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ag_data', '0003_errorlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='errorlog',
            name='error_code',
            field=models.CharField(choices=[('UNKNOWN_FORMAT', 'Unknown Format'), ('MISSING_COLUMN', 'Missing Column'), ('MISSING_FIELD_IN_RAW_READING', 'Missing Field In Raw Reading'), ('INVALID_COLUMN_NAME', 'Invalid Column Name'), ('INVALID_COLUMN_VALUE', 'Invalid Column Value'), ('INVALID_FIELD_IN_RAW_READING', 'Invalid Field In Raw Reading'), ('FORMULA_PROCESS_MEASUREMENT_ERROR', 'Error When Formula Processing Measurement'), ('EXTRANEOUS_KEY_VALUE_PAIR_IN_MEASUREMENT', 'Extraneous Key-Value Pair In Measurement'), ('NO_ACTIVE_EVENT', 'No active event'), ('OTHER_ERROR', 'Other Error')], default='OTHER_ERROR', max_length=100),
        ),
    ]
# Generated by Django 2.2.6 on 2020-03-21 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mercury", "0013_auto_20200320_1706"),
    ]

    operations = [
        migrations.AddField(
            model_name="gfconfig",
            name="gf_dashboard_uid",
            field=models.CharField(default="9UF7VluWz", max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="gfconfig",
            name="gf_db_host",
            field=models.CharField(
                default="ec2-35-168-54-239.compute-1.amazonaws.com" ":5432",
                max_length=128,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="gfconfig",
            name="gf_db_name",
            field=models.CharField(default="d76k4515q6qv", max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="gfconfig",
            name="gf_db_pw",
            field=models.CharField(
                default="f45a1cfe8458ff9236ead8a7943eba31dcef761471e"
                "0d6d62b043b4e3d2e10e5",
                max_length=256,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="gfconfig",
            name="gf_db_username",
            field=models.CharField(default="qvqhuplbiufdyq", max_length=64),
            preserve_default=False,
        ),
    ]

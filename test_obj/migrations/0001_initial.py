# Generated by Django 3.1.14 on 2022-07-04 11:24

from django.db import migrations, models
import djongo.models.fields
import test_obj.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('msg', models.CharField(blank=True, max_length=200, null=True)),
                ('test', models.CharField(blank=True, max_length=200, null=True)),
                ('count', models.IntegerField(blank=True, null=True)),
                ('date_time_testing', models.DateTimeField(blank=True, null=True)),
                ('required_fields', models.CharField(default='abc', max_length=50)),
            ],
            options={
                'db_table': 'test',
            },
        ),
        migrations.CreateModel(
            name='TestEmbed',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('test_embed', djongo.models.fields.EmbeddedField(model_container=test_obj.models.TestAbs)),
                ('test_array', djongo.models.fields.ArrayField(model_container=test_obj.models.TestAbs)),
            ],
            options={
                'db_table': 'TestEmbed',
            },
        ),
    ]

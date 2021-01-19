# Generated by Django 3.1.5 on 2021-01-19 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spec', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExampleDocumentElement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('element_name', models.CharField(max_length=80)),
                ('example', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spec.exampledocument')),
            ],
            options={
                'db_table': 'example_elements',
            },
        ),
    ]

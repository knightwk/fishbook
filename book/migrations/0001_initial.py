# Generated by Django 2.2.14 on 2020-08-05 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bookname', models.CharField(max_length=100)),
                ('author', models.CharField(max_length=100)),
                ('binding', models.BooleanField(choices=[(0, '精装'), (1, '简装')])),
                ('publisher', models.CharField(max_length=100)),
                ('pubdate', models.DateField()),
                ('price', models.FloatField()),
                ('pages', models.IntegerField()),
                ('isbn', models.CharField(max_length=30)),
                ('summary', models.CharField(max_length=255)),
                ('image', models.ImageField(upload_to='uploads/%Y/%m')),
                ('add_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'book',
            },
        ),
    ]

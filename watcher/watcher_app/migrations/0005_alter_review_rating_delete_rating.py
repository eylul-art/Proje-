# Generated by Django 5.1.6 on 2025-02-23 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('watcher_app', '0004_actor_alter_review_rating_film_actors_customuser_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.DecimalField(decimal_places=1, default=0.0, max_digits=2),
        ),
        migrations.DeleteModel(
            name='Rating',
        ),
    ]

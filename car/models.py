from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from car.utils import minio_client


# Create your models here.


class File(models.Model):
    file = models.FileField()

    def __str__(self):
        return f"{self.file}"


class Part(models.Model):
    part_name = models.CharField(max_length=50, unique=True)
    part_file = models.ManyToManyField(File)

    def __str__(self):
        return f"{self.part_name}"


class Car(models.Model):
    manufacture = models.CharField(max_length=50)
    car_type = models.CharField(max_length=50)
    model = models.CharField(max_length=50, unique=True)
    parts = models.ManyToManyField(Part)

    def __str__(self):
        return f"{self.manufacture} - {self.model}"


@receiver(post_delete, sender=File)
def minio_delete_file(sender, instance, **kwargs):
    minio_client.remove_object('local-media', instance.file.name)


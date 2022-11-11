from django.db import models

class Category(models.Model):
    label = models.CharField(max_length=200)
    slug = models.SlugField()


    def __str__(self):
        return f'{self.label}({self.id})'

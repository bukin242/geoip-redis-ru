from redisco import models
from slugify import slugify


class City(models.Model):
    city = models.Attribute(required=True)
    slug = models.Attribute()
    region = models.Attribute()
    territory = models.Attribute()
    country = models.Attribute()
    coordinates = models.ListField(float)

    def save(self):
        self.slug = slugify(self.city)
        super(City, self).save()


class IP(models.Model):
    start_range = models.IntegerField(indexed=True)
    end_range = models.IntegerField(indexed=True)
    city = models.ReferenceField(City)

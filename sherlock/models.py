from django.conf import settings
from django.db import models
from managers import ChannelManager


class Channel(models.Model):

    name = models.CharField(
        max_length=250,
        help_text='Identifier: app:polls:model:poll:instance:1:field:question',
        unique=True, db_index=True

    )

    objects = ChannelManager()

    def __unicode__(self):
        return self.name

    # TODO Find a better way to validate whether a channel is model, instance or field related
    def get_model(self):
        identifiers = self.name.split(':')
        return models.get_model(identifiers[1], identifiers[3])

    def get_instance(self):
        identifiers = self.name.split(':')
        if self.is_instance():
            return self.get_model().objects.get(pk=identifiers[5])

    def is_model(self):
        return len(self.name.split(':')) == 4

    def is_instance(self):
        return len(self.name.split(':')) == 6

    def is_field(self):
        return len(self.name.split(':')) == 8


class Subscriber(models.Model):

    email = models.EmailField(unique=True)
    channels = models.ManyToManyField('Channel')

    def __unicode__(self):
        return self.email


for app in settings.INSTALLED_APPS:
    try:
        module_name = '%s.observers' % str(app)
        __import__(module_name)
    except ImportError:
        pass


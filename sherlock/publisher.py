from .base import Metaclass
from .models import Channel, Subscriber


class BasePublisher(object):

    __metaclass__ = Metaclass

    def on_field_change(self, instance, field):
        Channel.objects.create_for_field(instance, field)

    def _requires_authorisation(self, field):
        return hasattr(self._meta, 'requires_authorisation') \
            and field in self._meta.requires_authorisation

    def authorise(self, instance, *changes):
        print '==============> Authorising instance pk: %s' % instance.pk

    def _publish(self, instance, field=None, changes=None):
        identifier = Channel.objects.construct_identifier(instance=instance, field=field)
        if self._meta.email:
            subscribers = Subscriber.objects.filter(channels__name__in=[identifier])
            self.send_email(subscribers, instance, field, changes)

    def send_email(subscribers, instance, field=None, changes=None):
        raise NotImplementedError

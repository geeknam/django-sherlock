from .base import Metaclass
from .models import Channel, Subscriber


class BasePublisher(object):

    __metaclass__ = Metaclass

    def on_instance_change(self, instance, created, **kwargs):
        self._create_channel(instance)
        self.publish_instance_change(self, instance, created, **kwargs)

    def on_field_change(self, instance, field, **kwargs):
        changes = kwargs.get('changes')
        publish_method = getattr(self, 'publish_%s' % field, self._publish)
        identifier = self._create_channel(instance, field)
        if not self._requires_authorisation(field):
            publish_method(instance, field, changes, identifier)
        else:
            self.authorise(instance, *changes)

    def _create_channel(self, instance, field=None):
        Channel.objects.create_for_field(instance, field)

    def _requires_authorisation(self, field):
        return hasattr(self._meta, 'requires_authorisation') \
            and field in self._meta.requires_authorisation

    def authorise(self, instance, *changes):
        # TODO: figure out the authorisation process
        print '==============> Authorising instance pk: %s' % instance.pk

    def _publish(self, instance, field, changes, identifier):
        if self._meta.email:
            subscribers = Subscriber.objects.filter(channels__name__in=[identifier])
            emails = [sub.email for sub in subscribers]
            self.send_email(emails, instance, field, changes)

    def send_email(subscribers, instance, field=None, changes=None):
        """
        Sends emails to all subscribers, context is provided
        """
        raise NotImplementedError

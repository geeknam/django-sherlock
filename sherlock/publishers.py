from .base import Metaclass
from .models import Channel, Subscriber


class BasePublisher(object):

    __metaclass__ = Metaclass

    def on_instance_change(self, instance, created, **kwargs):
        """
        Called when model observer receives a 'post_save' signal
        """
        identifier, channel = self._create_channel(instance)

        publish_method = getattr(self, 'publish_instance_change', None)
        if publish_method:
            publish_method(self, instance, created)
        else:
            self._publish(instance, identifier, created=created)

    def on_instance_delete(self, instance, **kwargs):
        # TODO: Remove the channels
        identifier, channel = self._create_channel(instance)
        self._publish(instance, identifier, deleted=True)

    def on_field_change(self, instance, field, **kwargs):
        """
        Called when an observed field has changed
        """
        changes = kwargs.get('changes')
        publish_method = getattr(self, 'publish_%s_change' % field, self._publish)
        identifier, channel = self._create_channel(instance, field)
        if not self._requires_authorisation(field):
            publish_method(instance, identifier, field=field, changes=changes)
        else:
            self.authorise(instance, *changes)

    def _create_channel(self, instance, field=None):
        return Channel.objects.create_channel(instance=instance, field=field)

    def _requires_authorisation(self, field):
        return hasattr(self._meta, 'requires_authorisation') \
            and field in self._meta.requires_authorisation

    def authorise(self, instance, *changes):
        # TODO: figure out the authorisation process
        print '==============> Authorising instance pk: %s' % instance.pk

    def _publish(self, instance, identifier, **context):
        """
        Figures out details of subscribers and publishes the notification.
        send_email() method has to be implemented
        """
        if hasattr(self._meta, 'email') and self._meta.email:
            subscribers = Subscriber.objects.filter(channels__name__in=[identifier])
            emails = [sub.email for sub in subscribers]
            self.send_email(emails, instance, **context)

    def send_email(subscribers, instance, **context):
        """
        Sends emails to all subscribers, context is provided
        """
        raise NotImplementedError

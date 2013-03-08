from .base import Metaclass
from .storage import RedisTempStore
from django.db.models.signals import post_save, pre_delete

default_signals = {
    'post_save': post_save,
    'pre_delete': pre_delete
}


class Observer(object):

    __metaclass__ = Metaclass

    def get_app_label(self):
        return self._meta.model._meta.app_label

    def get_model_name(self):
        return self.get_model()

    def get_model(self):
        return self._meta.model

    def get_fields(self):
        """
        Get all watched fields (declared in Meta class)
        """
        return self._meta.fields


class ModelObserver(Observer):
    """
    Observer that listens to some built-in and custom signals.
    Receivers should be named as RECEIVERNAME_receiver
    where RECEIVERNAME is the name of the receiver.
        E.g: a receiver for 'post_save signal' would be 'post_save_receiver'
    """
    def __init__(self, *args, **kwargs):
        custom_signals = kwargs.get('custom_signals', {})

        custom_signals.update(default_signals)
        for signal_name, signal in custom_signals.items():
            signal_receiver = getattr(self, '%s_receiver' % signal_name, None)
            if signal_receiver:
                # weak=False stops the receiver from being garbage collected
                signal.connect(signal_receiver, sender=self.get_model(), weak=False)

    def post_save_receiver(self, sender, instance, created, **kwargs):
        self.publisher.on_instance_change(instance, created, **kwargs)


class ObjectObserver(ModelObserver):
    """
    Model instance observer that tracks changes of defined fields.
    """
    def __init__(self, storage=RedisTempStore, *args, **kwargs):
        super(ObjectObserver, self).__init__(*args, **kwargs)

        timeout = kwargs.get('tempstore_timeout', None)
        tempstore_settings = {
            'observer': self,
            'prefix': 'sherlock:tempstore:%s:%s' % (self.get_app_label(), self.get_model_name()),
        }
        if timeout:
            tempstore_settings.update({'timeout': timeout})

        self.storage_client = storage(**tempstore_settings)

    def get_instance_field_value(self, instance, field_name):
        """
        Get field value of an instance, handles ForeignKey using pk
        """
        field = self.get_model()._meta.get_field_by_name(field_name)[0]
        field_type = field.get_internal_type()
        field_value = getattr(instance, field_name, None)
        if field_type in ('ForeignKey', ):
            return getattr(instance, field_name).pk if field_value else field_value
        else:
            return getattr(instance, field_name) if field_value else field_value

    def post_save_receiver(self, sender, instance, created, **kwargs):
        if not created:
            for observed_field in self.get_fields():
                changes = self.storage_client.get_changes(instance, observed_field)
                if changes:
                    self.publisher.on_field_change(
                        instance, observed_field, changes=changes
                    )

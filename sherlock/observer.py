from .base import ObserverMetaclass
from .storage import HashTempStore
from django.db.models.signals import post_save, pre_delete


default_signals = {
    'post_save': post_save,
    'pre_delete': pre_delete
}


class Observer(object):

    __metaclass__ = ObserverMetaclass

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

    def __init__(self, custom_signals={}):
        custom_signals.update(default_signals)
        for signal_name, signal in custom_signals.items():
            signal_receiver = getattr(self, '%s_receiver' % signal_name, None)
            if signal_receiver:
                signal.connect(signal_receiver, sender=self.get_model(), weak=False)


class ObjectObserver(ModelObserver):

    def __init__(self, custom_signals={}):
        super(ObjectObserver, self).__init__(custom_signals)
        self.storage_client = HashTempStore(
            prefix='sherlock:tempstore:%s:%s' % (self.get_app_label(), self.get_model_name())
        )

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

    def save_state(self, instance, field_name):
        hash_field_name = str(instance.pk)
        value = self.get_instance_field_value(instance, field_name)
        self.storage_client.set(
            field_name, {hash_field_name: value}
        )

    def get_state(self, instance, field_name):
        return self.storage_client.get(field_name, str(instance.pk))

    def get_changes(self, instance, field_name):
        previous = self.get_state(instance, field_name)
        current = self.get_instance_field_value(instance, field_name)
        if previous != current:
            self.save_state(instance, field_name)
            return [previous, current]
        return []

    def post_save_receiver(self, sender, instance, created, **kwargs):
        if not created:
            for observed_field in self.get_fields():
                on_change_method = getattr(self, '%s_on_changed' % observed_field, None)
                changes = self.get_changes(instance, observed_field)
                if on_change_method and changes:
                    on_change_method(*changes)



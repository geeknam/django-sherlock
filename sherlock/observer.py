from .base import ObserverMetaclass
from .storage import HashTempStore
from django.db.models.signals import post_save


class Observer(object):

    __metaclass__ = ObserverMetaclass

    def get_app_label(self):
        return self._meta.model._meta.app_label

    def get_model_name(self):
        return self.get_model()

    def get_model(self):
        return self._meta.model

    def get_fields(self):
        return self._meta.fields


class ModelObserver(Observer):

    def __init__(self):
        post_save.connect(self.post_save_receiver, sender=self._meta.model, weak=False)

    def post_save_receiver(self, sender, instance, **kwargs):
        raise NotImplementedError


class ObjectObserver(ModelObserver):

    def __init__(self):
        super(ObjectObserver, self).__init__()
        self.storage_client = HashTempStore(
            prefix='tempstore:%s:%s' % (self.get_app_label(), self.get_model_name())
        )

    def save_state(self, instance, field_name):
        hash_field_name = str(instance.pk)
        value = getattr(instance, field_name, None)
        self.storage_client.set(
            field_name, {hash_field_name: value}
        )

    def get_state(self, instance, field_name):
        return self.storage_client.get(field_name, str(instance.pk))

    def get_changes(self, instance, field_name):
        previous = self.get_state(instance, field_name)
        current = getattr(instance, field_name)
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



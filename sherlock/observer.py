from .base import ObserverMetaclass
from django.db.models.signals import post_save


class Observer(object):

    __metaclass__ = ObserverMetaclass

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

    def has_changed(self, field_name):
        raise NotImplementedError

    def post_save_receiver(self, sender, instance, created, **kwargs):
        if not created:
            for observed_field in self.get_fields():
                on_change_method = getattr(self, '%s_on_changed' % observed_field, None)
                print '=============>', on_change_method
                if on_change_method and self.has_changed(observed_field):
                    on_change_method()



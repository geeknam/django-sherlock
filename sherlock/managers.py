from django.db import models


class ChannelManager(models.Manager):

    # TODO: find cleaner way?
    def construct_identifier(self, **kwargs):
        model = kwargs.get('model', None)
        instance = kwargs.get('instance', None)
        field = kwargs.get('field', None)

        if model:
            model_name = model._meta.object_name.lower()
            app_label = model._meta.app_label
            return 'app:%s:model:%s' % (app_label, model_name)

        app_label = instance.__class__._meta.app_label
        model_name = instance.__class__._meta.object_name.lower()

        identifier = 'app:%s:model:%s:instance:%s'
        variables = [app_label, model_name, instance.pk]
        if field:
            if not hasattr(instance, field):
                raise AttributeError
            identifier += ':field:%s'
            variables.append(field)
        variables = tuple(variables)
        return identifier % variables

    def create_channel(self, **kwargs):
        identifier = self.construct_identifier(**kwargs)
        channel, created = self.get_or_create(name=identifier)

        return identifier, channel

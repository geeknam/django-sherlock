from django.db import models


class ChannelManager(models.Manager):

    def construct_identifier(self, **kwargs):
        instance = kwargs.get('instance', None)
        field = kwargs.get('field', None)

        app_label = instance.__class__._meta.app_label
        model_name = instance.__class__._meta.object_name.lower()

        identifier = 'app:%s:model:%s:instance:%s'
        variables = [app_label, model_name, instance.pk]
        if field:
            identifier += ':field:%s'
            variables.append(field)
        variables = tuple(variables)
        return identifier % variables

    def create_for_field(self, instance, field):
        identifier = self.construct_identifier(instance=instance, field=field)
        self.get_or_create(name=identifier)

        return identifier

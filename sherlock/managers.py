from django.db import models
from django.contrib.contenttypes.models import ContentType


class ChannelManager(models.Manager):

    def construct_identifier(self, **kwargs):
        instance = kwargs.get('instance', None)
        field = kwargs.get('field', None)

        content_type = ContentType.objects.get_for_model(instance.__class__)

        identifier = 'app:%s:model:%s:instance:%s:field:%s' % (
            content_type.app_label, content_type.model, instance.pk, field
        )
        return identifier

    def create_for_field(self, instance, field):
        identifier = self.construct_identifier(instance=instance, field=field)
        self.get_or_create(name=identifier)
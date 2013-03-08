
from django.contrib import admin
from polls import models
from .signals import test_signal


def send_signal(modeladmin, request, queryset):
    test_signal.send_robust(
        sender=modeladmin.model,
        objects=queryset
    )


class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'pub_date')

    actions = (send_signal, )

admin.site.register(models.Poll, PollAdmin)
admin.site.register(models.Choice)

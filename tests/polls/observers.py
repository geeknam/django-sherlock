from sherlock.observer import ObjectObserver, ModelObserver
from sherlock.publisher import BasePublisher
from .models import Poll, Choice


class PollPublisher(BasePublisher):
    class Meta:
        # requires_authorisation = ('question', )
        # sse_channels = ('all_events', )
        email = True

    def send_email(self, emails, instance, field=None, changes=None):
        print '=========> Sending email to: %s' % emails
        print '==============> Instance pk: %s' % instance.pk
        print '==============> Changes: %s' % changes

    def publish_question(self, instance, field, changes):
        print '==============> Instance pk: %s' % instance.pk
        print '==============> Field: %s' % field
        print '==============> Changes: %s' % changes


class PollModelObserver(ModelObserver):
    publisher = PollPublisher()

    class Meta:
        model = Poll


class PollObserver(ObjectObserver):
    publisher = PollPublisher()

    class Meta:
        model = Poll
        fields = ('question', )


class ChoiceObserver(ObjectObserver):

    class Meta:
        model = Choice
        fields = ('poll', )

poll_model_observer = PollModelObserver()
poll_observer = PollObserver()
choice_observer = ChoiceObserver()

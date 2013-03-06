from sherlock.observer import ObjectObserver
from sherlock.publisher import BasePublisher
from .models import Poll, Choice


class PollPublisher(BasePublisher):
    class Meta:
        # requires_authorisation = ('question', )
        email = True
        # sse_channels = ('all_events', )

    def send_email(self, emails, instance, field=None, changes=None):
        print '=========> Sending email to: %s' % emails
        print '==============> Instance pk: %s' % instance.pk
        print '==============> Changes: %s' % changes

    # def publish_question(self, instance, previous, current):
    #     print '==============> Instance pk: %s' % instance.pk
    #     print '==============> Previous: %s' % previous
    #     print '==============> Current: %s' % current


class PollObserver(ObjectObserver):
    publisher = PollPublisher()

    class Meta:
        model = Poll
        fields = ('question', )


class ChoiceObserver(ObjectObserver):

    class Meta:
        model = Choice
        fields = ('poll', )


poll_observer = PollObserver()
choice_observer = ChoiceObserver()

from sherlock.observers import ObjectObserver, ModelObserver
from sherlock.publishers import BasePublisher
from .models import Poll, Choice
from .signals import test_signal

custom_signals = {
    'test_signal': test_signal
}


class PollPublisher(BasePublisher):
    class Meta:
        # requires_authorisation = ('question', )
        # sse_channels = ('all_events', )
        email = True

    def send_email(self, emails, instance, **context):
        print '==============>', self
        print '==============> Sending email to: %s' % emails
        print '==============> Instance pk: %s' % instance.pk
        print '==============> Context: %s' % context

    def publish_question(self, instance, identifier, **context):
        print '==============>', self
        print '==============> Instance pk: %s' % instance.pk
        print '==============> Identifier: %s' % identifier
        print '==============> Context: %s' % context


class PollModelObserver(ModelObserver):
    publisher = PollPublisher()

    class Meta:
        model = Poll

    def test_signal_receiver(self, sender, **kwargs):
        print '==============>', self
        print '==============> Sender: %s' % sender
        print '==============> Objects: %s' % kwargs['objects']


class PollObserver(ObjectObserver):
    publisher = PollPublisher()

    class Meta:
        model = Poll
        fields = ('question', )


class ChoiceObserver(ObjectObserver):

    class Meta:
        model = Choice
        fields = ('poll', )

poll_model_observer = PollModelObserver(custom_signals=custom_signals)
poll_observer = PollObserver()
choice_observer = ChoiceObserver()

from django.test import TestCase
from django.dispatch import Signal

from polls.models import Poll
from sherlock.observers import ModelObserver
from sherlock.publishers import BasePublisher
from sherlock.models import Channel
from .method_logger import method_logger


class ModelObserverTest(TestCase):

    def setUp(self):

        class PollPublisher(BasePublisher):
            class Meta:
                email = True

            def send_email(self, emails, instance, **context):
                pass

        class PollModelObserver(ModelObserver):
            publisher = PollPublisher()

            class Meta:
                model = Poll

        self.observer = PollModelObserver()
        self.publisher = self.observer.publisher
        self.publisher.send_email = method_logger(self.publisher.send_email)
        self.publisher.on_instance_change = method_logger(self.publisher.on_instance_change)

    def tearDown(self):
        del self.observer
        del self.publisher

    def test_channel_created(self):
        poll = Poll.objects.create(question='What is going on?')
        identifier = Channel.objects.construct_identifier(instance=poll)
        self.assertIsInstance(Channel.objects.get(name=identifier), Channel)
        poll.delete()

    def test_send_email(self):
        poll = Poll.objects.create(question='What is going on?')
        self.assertTrue(self.publisher.send_email.was_called)
        poll.delete()

    def test_send_email_not_called(self):
        self.publisher._meta.email = False
        poll = Poll.objects.create(question='What is going on?')
        self.assertFalse(self.publisher.send_email.was_called)
        poll.delete()

    def test_send_email_context(self):
        poll = Poll.objects.create(question='What is going on?')
        expected_context_for_create = {
            'args': ([], poll),
            'kwargs': {'created': True}
        }
        expected_context_for_update = {
            'args': ([], poll),
            'kwargs': {'created': False}
        }
        self.assertEqual(self.publisher.send_email.context, expected_context_for_create)
        poll.question = 'New question?'
        poll.save()
        self.assertEqual(self.publisher.send_email.context, expected_context_for_update)
        poll.delete()

    def test_on_instance_change(self):
        poll = Poll.objects.create(question='What is going on?')
        self.assertTrue(self.publisher.on_instance_change.was_called)
        poll.delete()


class CustomSignalTest(TestCase):

    def test_custom_signal(self):

        class PollPublisher(BasePublisher):
            pass

        class PollModelObserver(ModelObserver):
            publisher = PollPublisher()

            class Meta:
                model = Poll

            def my_signal_receiver(self, sender, **kwargs):
                self.do_something(sender, my_arg=kwargs['my_arg'])

            def do_something(self, sender, **kwargs):
                pass

        my_signal = Signal(providing_args=['my_arg'])
        custom_signals = {
            'my_signal': my_signal
        }

        self.observer = PollModelObserver(custom_signals=custom_signals)
        self.publisher = self.observer.publisher
        self.observer.do_something = method_logger(self.observer.do_something)

        self.assertFalse(self.observer.do_something.was_called)
        my_signal.send_robust(sender=Poll, my_arg='Test argument')
        self.assertTrue(self.observer.do_something.was_called)

        self.assertEqual(self.observer.do_something.context['args'], (Poll, ))
        self.assertEqual(
            self.observer.do_something.context['kwargs'], {'my_arg': 'Test argument'}
        )
        del self.observer
        del self.publisher

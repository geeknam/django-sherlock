from django.test import TestCase
from polls.models import Poll
from sherlock.observers import ModelObserver
from sherlock.publishers import BasePublisher
from sherlock.models import Channel
from .method_logger import method_logger


class ModelObserverTest(TestCase):

    def setUp(self):
        def callback(*args, **kwargs):
            return {
                'args': args,
                'kwargs': kwargs
            }

        class PollPublisher(BasePublisher):
            class Meta:
                email = True

            def send_email(self, emails, instance, **context):
                print 'PollPublisher.send_email was called with context: %s' % context

        class PollModelObserver(ModelObserver):
            publisher = PollPublisher()

            class Meta:
                model = Poll

        self.publisher = PollModelObserver().publisher
        self.publisher.send_email = method_logger(self.publisher.send_email)


    def test_channel_created(self):
        poll = Poll.objects.create(question='What is going on?')
        identifier = Channel.objects.construct_identifier(instance=poll)
        self.assertIsInstance(Channel.objects.get(name=identifier), Channel)
        poll.delete()

    def test_send_email(self):
        poll = Poll.objects.create(question='What is going on?')
        self.assertTrue(self.publisher.send_email.was_called)
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
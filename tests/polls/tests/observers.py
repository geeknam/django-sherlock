from django.test import TestCase
from polls.models import Poll
from sherlock.observers import ModelObserver, ObjectObserver
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




class ObjectObserverTest(TestCase):

    def test_publish_default(self):

        class PollPublisher(BasePublisher):
            class Meta:
                email = True

            def send_email(self, emails, instance, **context):
                pass

        class PollObserver(ObjectObserver):
            publisher = PollPublisher()

            class Meta:
                model = Poll
                fields = ('question', )

        self.observer = PollObserver()
        self.publisher = self.observer.publisher
        self.publisher.send_email = method_logger(self.publisher.send_email)
        self.publisher.on_field_change = method_logger(self.publisher.on_field_change)

        poll = Poll.objects.create(question='What is going on?')

        old_question = 'Old question?'
        new_question = 'New question?'

        poll.question = old_question
        poll.save()

        poll.question = new_question
        poll.save()

        self.assertTrue(self.publisher.on_field_change.was_called)
        self.assertEqual(self.publisher.send_email.context['args'], ([], poll))
        kwargs = {
            'field': 'question',
            'changes': {
                'current': new_question,
                'previous': old_question
            }
        }
        for k, v in kwargs.items():
            self.assertIn(k, self.publisher.send_email.context['kwargs'])
            self.assertEqual(v, self.publisher.send_email.context['kwargs'][k])

        poll.delete()
        self.observer.disconnect_signals()


    def test_publish_custom(self):

        class PollPublisher(BasePublisher):

            def publish_question(self, instance, identifier, **context):
                pass

        class PollObserver(ObjectObserver):
            publisher = PollPublisher()

            class Meta:
                model = Poll
                fields = ('question', )

        self.observer = PollObserver()
        self.publisher = self.observer.publisher
        self.publisher.publish_question = method_logger(self.publisher.publish_question)
        self.publisher.on_field_change = method_logger(self.publisher.on_field_change)

        poll = Poll.objects.create(question='What is going on?')

        old_question = 'Old question?'
        new_question = 'New question?'

        poll.question = old_question
        poll.save()

        poll.question = new_question
        poll.save()

        self.assertTrue(self.publisher.on_field_change.was_called)
        self.assertEqual(
            self.publisher.publish_question.context['args'],
            (poll, Channel.objects.construct_identifier(instance=poll, field='question'))
        )
        kwargs = {
            'field': 'question',
            'changes': {
                'current': new_question,
                'previous': old_question
            }
        }
        for k, v in kwargs.items():
            self.assertIn(k, self.publisher.publish_question.context['kwargs'])
            self.assertEqual(v, self.publisher.publish_question.context['kwargs'][k])

        poll.delete()
        self.observer.disconnect_signals()

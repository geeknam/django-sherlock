from django.test import TestCase
from polls.models import Poll
from sherlock.observers import ObjectObserver
from sherlock.publishers import BasePublisher
from sherlock.models import Channel
from .method_logger import method_logger


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
        del self.observer.signals

    def test_publish_custom(self):

        class PollPublisher(BasePublisher):

            def publish_question_change(self, instance, identifier, **context):
                pass

        class PollObserver(ObjectObserver):
            publisher = PollPublisher()

            class Meta:
                model = Poll
                fields = ('question', )

        self.observer = PollObserver()
        self.publisher = self.observer.publisher
        self.publisher.publish_question_change = method_logger(self.publisher.publish_question_change)
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
            self.publisher.publish_question_change.context['args'],
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
            self.assertIn(k, self.publisher.publish_question_change.context['kwargs'])
            self.assertEqual(v, self.publisher.publish_question_change.context['kwargs'][k])

        poll.delete()
        del self.observer.signals
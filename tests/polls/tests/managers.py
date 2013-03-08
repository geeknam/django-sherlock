from django.test import TestCase
from polls.models import Poll
from sherlock.models import Channel


class ChannelManagerTest(TestCase):

    def setUp(self):
        self.poll = Poll.objects.create(question='What is going on?')

    def tearDown(self):
        self.poll.delete()

    def test_construct_identifier_for_instance(self):
        identifier = Channel.objects.construct_identifier(instance=self.poll)
        self.assertEqual(identifier, 'app:polls:model:poll:instance:1')

    def test_construct_identifier_for_field(self):
        identifier = Channel.objects.construct_identifier(instance=self.poll, field='question')
        self.assertEqual(identifier, 'app:polls:model:poll:instance:1:field:question')

    def test_construct_identifier_for_non_existing_field(self):
        with self.assertRaises(AttributeError):
            Channel.objects.construct_identifier(instance=self.poll, field='foo')

    def test_create_field_for_instance(self):
        identifier = Channel.objects.create_channel(self.poll)
        self.assertEqual(identifier, 'app:polls:model:poll:instance:1')
        self.assertIsInstance(Channel.objects.get(name=identifier), Channel)

    def test_create_field_for_field(self):
        identifier = Channel.objects.create_channel(self.poll, 'question')
        self.assertEqual(identifier, 'app:polls:model:poll:instance:1:field:question')
        self.assertIsInstance(Channel.objects.get(name=identifier), Channel)

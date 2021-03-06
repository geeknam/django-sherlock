====================
django-sherlock
====================

.. image:: https://travis-ci.org/geeknam/django-sherlock.png?branch=master
        :target: https://travis-ci.org/geeknam/django-sherlock

django-sherlock is a customizable notifications framework for Django

Requirements
=============
* Django 1.3+
* redis (optional)


Basic usage
=============
Observing model instance changes::

    # polls/observers.py

    from django.dispatch import Signal
    from sherlock.observers import ObjectObserver, ModelObserver
    from sherlock.publishers import BasePublisher

    from polls.models import Poll

    test_signal = Signal(providing_args=['objects'])
    custom_signals = {
        'test_signal': test_signal
    }

    class PollPublisher(BasePublisher):
        class Meta:
            email = True

        def send_email(self, emails, instance, **context):
            pass

        def publish_question_change(self, instance, identifier, **context):
            """
            Called when `question` field has changed
            """ 
            pass

        def test_signal_received(self, **kwargs):
            pass


    class PollModelObserver(ModelObserver):
        publisher = PollPublisher()

        class Meta:
            model = Poll

        def test_signal_receiver(self, sender, **kwargs):
            """
            Receiver method called when a custom signal is sent.
            Can be delegated to a Publisher class.
            """
            self.publisher.test_signal_received(**kwargs)


    class PollObserver(ObjectObserver):
        publisher = PollPublisher()

        class Meta:
            model = Poll
            fields = ('question', )  # only observe `question` changes


    poll_model_observer = PollModelObserver(custom_signals=custom_signals)
    poll_observer = PollObserver()


Subscribing to changes::

    from sherlock.utils import subscribe
    from polls.models import Poll

    # Subscribe to a model
    subscribe('nam@namis.me', model=Poll)

    # Subscribe to a field of an instance
    subscribe('nam@namis.me', instance=poll, field='question')


Customisation
===============
django-sherlock implements a temporary storage which stores values of
fields that are tracked. These values are used for the comparison when
a field is updated. By default, django-sherlock uses redis hashes to store these values.
It is however possible to implement your own storage class if you're using Memcache or MongoDB.

Write your own storage backend by extending BaseStorage class. Example::

    from sherlock.storage import BaseStorage

    class MemcacheStorage(BaseStorage):

        def get(self, instance, field_name):
            pass

        def set(self, instance, field_name, value):
            pass

        def get_changes(self, instance, field_name):
            """
            Compare previous and current value of the field.
            Return previous and current value in a dict if there are changes:
            dict(
                previous='previous_value',
                current='current_value'
            )
            """
            pass


Using the custom storage backend::

    from sherlock.observers import ObjectObserver

    class PollObserver(ObjectObserver):
        publisher = PollPublisher()

        class Meta:
            model = Poll
            fields = ('question', )

    poll_observer = PollObserver(storage=MemcacheStorage)
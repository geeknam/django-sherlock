====================
django-sherlock
====================

.. image:: https://travis-ci.org/geeknam/django-sherlock.png?branch=master
        :target: https://travis-ci.org/geeknam/django-sherlock

django-sherlock is a customizable notifications framework for Django

Requirements
=============
* Django 1.3+
* redis


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
            fields = ('question', )  # only observe `question` changes


    poll_model_observer = PollModelObserver(custom_signals=custom_signals)
    poll_observer = PollObserver()


Subscribing to changes::
To be continued...
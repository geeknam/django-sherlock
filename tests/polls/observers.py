# from sherlock.observers import ObjectObserver, ModelObserver
# from .models import Poll, Choice
# from .signals import test_signal
# from .publishers import PollPublisher

# custom_signals = {
#     'test_signal': test_signal
# }


# class PollModelObserver(ModelObserver):
#     publisher = PollPublisher()

#     class Meta:
#         model = Poll

#     def test_signal_receiver(self, sender, **kwargs):
#         print '==============>', self
#         print '==============> Sender: %s' % sender
#         print '==============> Objects: %s' % kwargs['objects']


# class PollObserver(ObjectObserver):
#     publisher = PollPublisher()

#     class Meta:
#         model = Poll
#         fields = ('question', )


# class ChoiceObserver(ObjectObserver):

#     class Meta:
#         model = Choice
#         fields = ('poll', )

# poll_model_observer = PollModelObserver(custom_signals=custom_signals)
# poll_observer = PollObserver()
# choice_observer = ChoiceObserver()

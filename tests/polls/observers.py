from sherlock.observer import ModelObserver, ObjectObserver
from .models import Poll


# class PollObserver(ModelObserver):

#     class Meta:
#         model = Poll

#     def post_save_receiver(self, sender, instance, **kwargs):
#         self.receiver_task.delay(sender=sender, instance_pk=instance.pk)

#     @task()
#     def receiver_task(self, sender, instance_pk):
#         print '==========> %s: %s' % (sender, instance_pk)


class PollObserver(ObjectObserver):

    class Meta:
        model = Poll
        fields = ('question', )

    def has_changed(self, field_name):
        return True

    def question_on_changed(self, previous, current):
        print '==========> Previous: %s' % previous
        print '==========> Previous: %s' % current


poll_observer = PollObserver()

from sherlock.publishers import BasePublisher


class PollPublisher(BasePublisher):
    class Meta:
        # requires_authorisation = ('question', )
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

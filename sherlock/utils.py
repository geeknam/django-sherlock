from models import Subscriber, Channel


def subscribe(email, **kwargs):
    identifier, channel = Channel.objects.create_channel(**kwargs)

    subscriber, created = Subscriber.objects.get_or_create(email=email)
    subscriber.channels.add(channel)
    subscriber.save()

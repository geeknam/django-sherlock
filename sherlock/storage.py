import redis
from django.conf import settings
try:
    import cPickle as pickle
except ImportError:
    import pickle


class BaseStorage(object):

    def get(self, instance, field_name):
        raise NotImplementedError

    def set(self, observer, instance, field_name):
        raise NotImplementedError


class HashTempStore(object):
    def __init__(self, prefix=None, timeout=60 * 60 * 24):
        self.timeout = timeout
        self.prefix = prefix
        self._client = redis.StrictRedis(**settings.REDIS_SETTINGS)

    def make_hash_key(self, key):
        return '%s:%s' % (self.prefix, key)

    def get(self, key, field):
        hash_key = self.make_hash_key(key)
        value = self._client.hget(hash_key, field)
        if value is None:
            return
        return pickle.loads(value)

    def set(self, key, mapping):
        assert isinstance(mapping, dict)
        hash_key = self.make_hash_key(key)
        mapping = dict([(m[0], pickle.dumps(m[1])) for m in mapping.items()])
        self._client.hmset(hash_key, mapping)
        self._client.expire(hash_key, self.timeout)


class RedisTempStore(HashTempStore, BaseStorage):
    """
    Wrapper class around HashTempStore to interface with observer class
    """

    def get(self, instance, field_name):
        """
        Gets field value from temporary storage.
        """
        return super(RedisTempStore, self).get(field_name, str(instance.pk))

    def set(self, observer, instance, field_name):
        """
        Temporarily stores field value. Timout can be define.
        Used in comparison when the the field changes.
        """
        hash_field_name = str(instance.pk)
        value = observer.get_instance_field_value(instance, field_name)
        super(RedisTempStore, self).set(
            field_name, {hash_field_name: value}
        )

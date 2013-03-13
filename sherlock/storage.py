from django.conf import settings
try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import redis
except ImportError:
    pass


class BaseStorage(object):

    def __init__(self, *arg, **kwargs):
        self.observer = kwargs.get('observer', None)

    def get(self, instance, field_name):
        """
        Gets field value from temporary storage.
        """
        raise NotImplementedError

    def set(self, instance, field_name, value):
        """
        Temporarily stores field value. Timout can be define.
        Used in comparison when the the field changes.
        """
        raise NotImplementedError

    def get_changes(self, instance, field_name):
        """
        Compare previous and current value of the field.
        Return previous and current value in a dict if there are changes:
        dict(
            previous='previous_value',
            current='current_value'
        )
        """
        raise NotImplementedError


class HashTempStore(object):
    """
    key/field                    | instance1.pk | instance2.pk |
    prefix:app:model:field1      |    value1    |    value2    |
    prefix:app:model:field2      |    value1    |    value2    |
    """

    def __init__(self, *args, **kwargs):
        self.timeout = kwargs.get('timeout', 60 * 60 * 24)
        self.prefix = kwargs.get('prefix', None)
        self._client = redis.StrictRedis(**settings.REDIS_SETTINGS)
        super(HashTempStore, self).__init__(*args, **kwargs)

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
        return super(RedisTempStore, self).get(field_name, str(instance.pk))

    def set(self, instance, field_name, value):
        hash_field_name = str(instance.pk)
        super(RedisTempStore, self).set(
            field_name, {hash_field_name: value}
        )

    def get_changes(self, instance, field_name):
        previous = self.get(instance, field_name)
        current = self.observer.get_instance_field_value(instance, field_name)
        if previous != current:
            self.set(instance, field_name, current)
            return {
                'previous': previous,
                'current': current
            }
        return None

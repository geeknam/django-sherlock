import redis
from django.conf import settings
try:
    import cPickle as pickle
except ImportError:
    import pickle


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

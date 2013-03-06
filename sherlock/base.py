

class Option(object):

    def __new__(cls, meta=None):
        # Return a new class base on ourselves
        attrs = dict(
            (name, getattr(meta, name))
            for name in dir(meta)
            if not name[0] == '_'
        )
        return object.__new__(type('Option', (cls,), attrs))


class Metaclass(type):

    def __new__(cls, name, bases, attrs):
        observer_class = super(Metaclass, cls).__new__(cls, name, bases, attrs)
        opts = getattr(observer_class, 'Meta', None)
        observer_class._meta = Option(opts)

        return observer_class

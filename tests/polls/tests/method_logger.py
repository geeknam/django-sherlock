

class method_logger(object):
    def __init__(self, method):
        self.method = method
        self.was_called = False
        self.context = {}

    def __call__(self, *args, **kwargs):
        self.method(*args, **kwargs)
        self.was_called = True
        self.context = {
            'args': args,
            'kwargs': kwargs
        }

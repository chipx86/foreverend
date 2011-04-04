class Signal(object):
    def __init__(self):
        self.callbacks = []

    def connect(self, callback):
        self.callbacks.append(callback)

    def emit(self, *args, **kwargs):
        result = False

        for callback in self.callbacks:
            result = result or callback(*args, **kwargs)

        return result

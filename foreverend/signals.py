class SignalConnection(object):
    def __init__(self, signal, cb):
        self.signal = signal
        self.cb = cb

    def disconnect(self):
        self.signal.callbacks.remove(self.cb)


class Signal(object):
    def __init__(self):
        self.callbacks = []

    def connect(self, callback):
        self.callbacks.append(callback)
        return SignalConnection(self, callback)

    def emit(self, *args, **kwargs):
        result = False

        for callback in self.callbacks:
            result = result or callback(*args, **kwargs)

        return result

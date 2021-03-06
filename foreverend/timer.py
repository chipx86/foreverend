from foreverend import get_engine


class Timer(object):
    def __init__(self, ms, cb, one_shot=False):
        self.engine = get_engine()
        self.ms = ms
        self.cb = cb
        self.tick_count_count = 0
        self.started = False
        self.paused_for_ms = 0
        self.unpause_cb = None
        self.one_shot = one_shot
        self.tick_cnx = None

        if ms > 0:
            self.start()

    def start(self):
        if not self.started:
            self.tick_count = 0
            self.paused_for_ms = 0
            self.unpause_cb = None
            self.tick_cnx = self.engine.tick.connect(self.on_tick)
            self.started = True

    def reset(self):
        self.tick_count = 0
        self.paused_for_ms = 0
        self.unpause_cb = None

        if self.ms > 0:
            self.start()

    def stop(self):
        if self.started:
            self.tick_cnx.disconnect()
            self.tick_cnx = None
            self.started = False

    def pause(self, ms, unpause_cb):
        self.paused_for_ms = ms
        self.unpause_cb = unpause_cb
        self.tick_count = 0

    def on_tick(self):
        self.tick_count += 1.0 / self.engine.FPS * 1000

        if self.paused_for_ms > 0 and self.tick_count >= self.paused_for_ms:
            self.paused_for_ms = 0
            self.unpause_cb()
        elif self.tick_count >= self.ms:
            self.tick_count = 0
            self.cb()

            if self.one_shot:
                self.stop()

from foreverend.signals import Signal


class EventBox(object):
    def __init__(self, area):
        self.area = area
        self.rects = []
        area.register_for_events(self)
        self.entered_objects = set()

        # Signals
        self.event_fired = Signal()
        self.object_moved = Signal()
        self.object_entered = Signal()
        self.object_exited = Signal()

    def watch_object_moves(self, obj):
        obj.moved.connect(lambda dx, dy: self.handle_object_move(obj))

    def handle_event(self, event):
        return self.event_fired.emit(event)

    def handle_object_move(self, obj):
        if obj.layer.area != self.area:
            return

        if obj.rect.collidelist(self.rects) != -1:
            if obj not in self.entered_objects:
                self.entered_objects.add(obj)
                self.object_entered.emit(obj)

            self.object_moved.emit(obj)
        elif obj in self.entered_objects:
            self.entered_objects.remove(obj)
            self.object_exited.emit(obj)

from timer import Timer

class TimerManager():
    def __init__(self):
        self.id_accumulator = 0
        self.list_of_timers = []
    
    def new_timer(self, end_time):
        new_timer = Timer(self.id_accumulator, end_time)
        self.list_of_timers.append(new_timer)
        self.id_accumulator += 1
        return self.id_accumulator - 1 # The ID of the created timer, not the new to-be-assigned ID
    
    def start_timer(self, id):
        self.list_of_timers[id].start()
    
    def stop_timer(self, id):
        self.list_of_timers[id].stop()
    
    def reset_timer(self, id):
        self.list_of_timers[id].reset()
    
    def set_new_end_time(self, id, new_time):
        self.list_of_timers[id].set_new_time(new_time)
    
    def update(self, dt):
        for timer in self.list_of_timers:
            timer.update(dt)
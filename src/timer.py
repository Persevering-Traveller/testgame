import pygame
import src.constants as constants

class Timer():
    def __init__(self, id, end_time = 0):
        self.id = id
        self.started = False
        self.accumulator = 0
        self.end_time = end_time
    
    def start(self):
        self.started = True

    def reset(self):
        self.accumulator = 0
    
    def stop(self):
        self.started = False
        self.reset()
    
    def set_new_time(self, new_time):
        self.stop()
        self.end_time = new_time
    
    def update(self, dt):
        if not self.started: return
        self.accumulator += dt

        if self.accumulator >= self.end_time:
            self.accumulator = 0
            pygame.event.post(pygame.Event(constants.CUSTOMEVENTS.TIMER_ENDED, {"id": self.id}))
            self.stop()
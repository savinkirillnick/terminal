from math import floor
from time import time


class ThreadTimer:

    def __init__(self):
        """Счетчик посекундного выполнения запросов по API и ограничения флуда."""
        self.last_time = floor(time())

    def check(self, t):
        if floor(t) == self.last_time:
            return False
        else:
            self.last_time = floor(t)
            return True

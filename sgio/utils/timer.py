import time

class Timer:
    timers = dict()

    def __init__(self, name=None, text='Elapsed time {:0.4f} seconds', logger=print):
        self._start_time = None
        self.name = name
        self.text = text
        self.logger = logger
        self.records = []

        if name:
            self.timers.setdefault(name, 0)

    def start(self):
        if self._start_time is not None:
            raise Exception(f"Timer is running.")

        self._start_time = time.perf_counter()

    def stop(self):
        if self._start_time is None:
            raise Exception(f"Timer is not running.")

        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None

        if self.logger:
            self.logger(self.text.format(elapsed_time))
        if self.name:
            self.timers[self.name] += elapsed_time
        self.records.append(elapsed_time)

        return elapsed_time



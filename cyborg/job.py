from asyncio import coroutine

from aiopipes import Pipeline
from aiopipes.pipeio import IterableIO
from aiopipes.monitor import ConsoleMonitor
from .task import Scraper


class Job(Pipeline):
    def __init__(self, *args, **kwargs):
        self._monitor = None
        super().__init__(*args, **kwargs)

    def __or__(self, other):
        if isinstance(other, Scraper):
            return super().__or__(other.runner)
        return super().__or__(other)

    @coroutine
    def start(self):
        if self.input is None:
            self.input = IterableIO([{}])

        start_future = super().start()

        if self._monitor:
            yield from self._monitor.monitor(start_future)
        else:
            yield from start_future

    def monitor(self):
        self._monitor = ConsoleMonitor(self)
        return self._monitor

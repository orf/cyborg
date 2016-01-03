from collections import Mapping
from asyncio import coroutine, iscoroutine

from aiopipes.runner import FunctionRunner
from .requester import Requester


requester = Requester()


class Scraper(object):
    def __init__(self, url_format):
        self.runner = None
        self.url_format = url_format

    def __call__(self, func):
        return ScraperRunner(func, self.url_format, requester)


class ScraperRunner(FunctionRunner):
    def __init__(self, func, url_format, requester=None):
        self.scraper_func = func
        self.url_format = url_format
        self.requester = requester or Requester()
        super().__init__(func=self.process_job)

    def _get_params(self, func, allowed_args=None):
        return super()._get_params(self.scraper_func, allowed_args)

    @coroutine
    def process_job(self, data, **kwargs):
        if not isinstance(data, Mapping):
            data = {"data": data}
        url = self.url_format.format(**data)
        response = yield from self.requester.get(url)

        if response is None:
            # The event loop has closed!
            return None

        result = self.scraper_func(data, response=response, **kwargs)
        if iscoroutine(result):
            result = yield from result
        return result

    @property
    def name(self):
        return self.scraper_func.__name__

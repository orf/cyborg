import asyncio
import logging
import json

import aiohttp
import lxml.html
import lxml.etree

from .selector import Selector

logger = logging.getLogger("requester")


class RequestError(RuntimeError):
    def __init__(self, url, *args, **kwargs):
        self.url = url
        super().__init__(*args, **kwargs)


class ServerError(RequestError):
    pass


class NotFoundError(RequestError):
    pass


class ResponseError(RequestError):
    pass


class HttpError(RequestError):
    def __init__(self, url, code):
        self.code = code
        super().__init__(url, "HTTP {0} encountered".format(self.code))


class Response(Selector):
    def __init__(self, response, content, node):
        self.response = response
        self.is_json = False

        try:
            self.content = json.loads(content)
            self.is_json = True
        except Exception:
            self.content = content

        super().__init__(node)

    def __getitem__(self, item):
        if self.is_json:
            return self.content[item]
        else:
            raise RuntimeError("Response is not JSON")

    def open_in_browser(self):
        import webbrowser
        import tempfile
        x = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        x.write(lxml.html.etree.tostring(self.document, pretty_print=True))
        x.close()
        webbrowser.open(x.name)
        print(x.name)


class Requester(object):
    def __init__(self, concurrency=5, error_contents="", not_found_contents="", event_loop=None):
        self.error_contents = error_contents
        self.not_found_contents = not_found_contents
        self.concurrency = concurrency
        self.semaphore = asyncio.BoundedSemaphore(concurrency)
        self.event_loop = event_loop or asyncio.get_event_loop()

    @asyncio.coroutine
    def get(self, url):
        attempts = 0

        while True:
            logger.info("Requesting {0}".format(url))
            with (yield from self.semaphore):
                if self.event_loop.is_closed():
                    return None

                try:
                    response = yield from aiohttp.request("GET", url, allow_redirects=True, loop=self.event_loop)
                except Exception as e:
                    logger.error("Could not retrieve {0}".format(url))
                    raise RequestError(url) from e

            if 500 < response.status < 599:
                if response.status == 503:
                    attempts += 1
                    if attempts < 4:
                        continue
                yield from response.close()
                raise HttpError(url, response.status)
            elif response.status == 404:
                yield from response.close()
                raise NotFoundError(url)

            data = yield from response.text()

            if self.error_contents and self.error_contents in data:
                raise ServerError(url)

            if self.not_found_contents and self.not_found_contents in data:
                raise NotFoundError(url)

            try:
                node = lxml.html.fromstring(data)
            except lxml.etree.ParseError as e:
                raise ResponseError(url) from e

            return Response(response, data, node)

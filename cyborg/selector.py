from functools import lru_cache
import logging
import lxml.html
from cssselect import HTMLTranslator


class SelectorException(RuntimeError):
    def __init__(self, selector, document):
        self.selector = selector
        self.doc = document


translator = HTMLTranslator()


@lru_cache()
def xpath(pattern):
    return translator.css_to_xpath(pattern)


logger = logging.getLogger("selector")
_notset = object


class Selector(object):
    def __init__(self, document):
        self.document = document
        self.translator = HTMLTranslator()

    def find(self, pattern):
        expression = xpath(pattern)
        results = [Selector(d) for d in self.document.xpath(expression)]
        if len(results) == 0:
            logger.warning("Selector {0} found 0 results".format(pattern))
        return results

    def get(self, pattern, default=_notset):
        expression = xpath(pattern)
        results = self.document.xpath(expression)
        try:
            return Selector(results[0])
        except IndexError as e:
            if default is not _notset:
                return default

            raise SelectorException(pattern, self.document) from e

    def has_class(self, cls):
        return cls in self.attr.get("class", "").split(" ")

    @property
    def attr(self):
        return dict(self.document.items())

    @property
    def text(self):
        return self.document.text_content()

    @property
    def parent(self):
        return Selector(self.document.getparent())

    @property
    def pretty(self):
        return lxml.html.etree.tostring(self.document, pretty_print=True).decode()

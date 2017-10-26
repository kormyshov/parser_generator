from lxml import html
from parser_result import Component, ParserResult, Encoder
import json


class FullPath(object):
    def __init__(self, xpath, attr):
        self.xpath = xpath
        self.attr = attr

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return self.xpath + "." + self.attr


class MarkupComponent(object):
    def __init__(self):
        self.type = None
        self.alignment = None
        self.page_url = None
        self.title = None

    def __str__(self):
        return json.dumps(self, cls=Encoder, ensure_ascii=False)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class MarkupSearchResult(MarkupComponent):
    def __init__(self):
        MarkupComponent.__init__(self)
        self.type = "SEARCH_RESULT"
        self.snippet = None
        self.view_url = None

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class MarkupWizardImage(MarkupComponent):
    def __init__(self):
        MarkupComponent.__init__(self)
        self.type = "WIZARD"
        self.wizard_type = "WIZARD_IMAGE"
        self.media_links = list()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Markup(object):
    def __init__(self):
        self.file = None
        self.components = list()

    def __str__(self):
        return json.dumps(self, cls=Encoder, ensure_ascii=False, indent=4)

    def add(self, component):
        self.components.append(component)

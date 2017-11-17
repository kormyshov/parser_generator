from lxml import html

from markups.search_markup import SearchMarkupSearchResult, FullPath, SearchMarkup, SearchMarkupWizardImage, SearchMarkupWizardNews, SearchMarkupAdv
from parser_result import ParserResult, Component
from parsers.parser import Parser


class YandexParser_v3(Parser):
    @staticmethod
    def get_index(parent, tag):
        index = 1
        for child in parent.iterchildren():
            if child == tag:
                return index
            if child.tag == tag.tag:
                index += 1
        return None

    @staticmethod
    def get_path(element):
        path = ""
        while element.tag != "html":
            path = "/" + element.tag + "[" + str(YandexParser_v3.get_index(element.getparent(), element)) + "]" + path
            element = element.getparent()
        path = "//html" + path
        return path

    def get_from_page(self, element, xpath, attr):
        tag = element.xpath(xpath)
        if len(tag) == 0:
            return ""
        tag = tag[0]
        attrs = ["href", "title", "style", "src"]
        if attr in attrs:
            if attr == "style":
                return tag.get("style").split("//")[1][:-2]
            return tag.get(attr)
        text = ""
        for i in tag.itertext():
            text += i
        return text

    def extract_search_result(self, element):
        search_result = SearchMarkupSearchResult()
        search_result.alignment = "LEFT"
        search_result.page_url = FullPath(YandexParser_v3.get_path(element) + "/h2/a", "href")
        search_result.title = FullPath(YandexParser_v3.get_path(element) + "/h2/a", "string")
        search_result.snippet = FullPath(YandexParser_v3.get_path(element) + "/div[2]/div[1]", "string")
        search_result.view_url = FullPath(YandexParser_v3.get_path(element) + "/div/div[1]/a[last()]", "href")
        return search_result

    def extract_adv(self, element):
        adv = SearchMarkupAdv()
        adv.alignment = "LEFT"
        adv.page_url = FullPath(YandexParser_v3.get_path(element) + "/h2/a", "href")
        adv.title = FullPath(YandexParser_v3.get_path(element) + "/h2/a", "string")
        adv.snippet = FullPath(YandexParser_v3.get_path(element) + "/div[@class='organic__content-wrapper clearfix']/div[1]", "string")
        adv.view_url = FullPath(YandexParser_v3.get_path(element) + "/div[@class='organic__subtitle typo typo_type_greenurl']/div[1]/a", "string")
        return adv

    def parse_search_result(self, element):
        search_result = Component()
        search_result.type = "SEARCH_RESULT"
        search_result.alignment = "LEFT"
        search_result.page_url = self.get_from_page(element, "./h2/a", "href")
        search_result.title = self.get_from_page(element, "./h2/a", "string")
        search_result.snippet = self.get_from_page(element, "./div[2]/div[1]", "string")
        search_result.view_url = self.get_from_page(element, "./div/div[1]/a[last()]", "href")
        return search_result

    def parse_adv(self, element):
        adv = Component()
        adv.type = "ADV"
        adv.alignment = "LEFT"
        adv.page_url = self.get_from_page(element, "./h2/a", "href")
        adv.title = self.get_from_page(element, "./h2/a", "string")
        adv.snippet = self.get_from_page(element, "./div[@class='organic__content-wrapper clearfix']/div[1]", "string")
        adv.view_url = self.get_from_page(element, "./div[@class='organic__subtitle typo typo_type_greenurl']/div[1]/a", "string")
        return adv

    def extract_wizard_image(self, element):
        wizard = SearchMarkupWizardImage()
        wizard.alignment = "LEFT"
        img_list = element.xpath("./div[2]/div/div/div/a")
        for img in img_list:
            wizard.media_links.append(FullPath(YandexParser_v3.get_path(img) + "/div[1]/div[1]", "style"))
        wizard.page_url = FullPath(YandexParser_v3.get_path(element) + "/div[1]/h2/a", "href")
        wizard.title = FullPath(YandexParser_v3.get_path(element) + "/div[1]/h2/a", "string")
        return wizard

    def parse_wizard_image(self, element):
        wizard = Component()
        wizard.type = "WIZARD"
        wizard.wizard_type = "WIZARD_IMAGE"
        wizard.alignment = "LEFT"
        img_list = element.xpath("./div[2]/div/div/div/a")
        wizard.media_links = list()
        for img in img_list:
            wizard.media_links.append(self.get_from_page(img, "./div[1]/div[1]", "style"))
        wizard.page_url = self.get_from_page(element, "./div[1]/h2/a", "href")
        wizard.title = self.get_from_page(element, "./div[1]/h2/a", "string")
        return wizard

    def extract_wizard_news(self, element):
        wizard = SearchMarkupWizardNews()
        wizard.alignment = "LEFT"
        wizard.page_url = FullPath(YandexParser_v3.get_path(element) + "/div[1]/h2/a[2]", "href")
        wizard.title = FullPath(YandexParser_v3.get_path(element) + "/div[1]/h2/a[2]", "string")
        return wizard

    def parse_wizard_news(self, element):
        wizard = Component()
        wizard.type = "WIZARD"
        wizard.wizard_type = "WIZARD_NEWS"
        wizard.alignment = "LEFT"
        wizard.page_url = self.get_from_page(element, "./div[1]/h2/a[2]", "href")
        wizard.title = self.get_from_page(element, "./div[1]/h2/a[2]", "string")
        return wizard

    def extract_markup(self, file_name):
        with open(file_name, "r") as file:
            tree = html.document_fromstring(file.read())
        markup = SearchMarkup()
        markup.file = file_name.split('/')[-1]
        block_list = tree.xpath("//html/body/div[3]/div/div[2]/div/div/ul/li/div")
        for block in block_list:
            if (len(block.xpath("./div[2]/div[2]")) > 0 and block.xpath("./div[2]/div[2]")[0].text == "реклама") or \
                    (len(block.xpath("./div[1]/div[2]")) > 0 and block.xpath("./div[1]/div[2]")[0].text == "реклама"):
                result = self.extract_adv(block)
                markup.add(result)
                continue
            if len(block.xpath("./h2/a")) > 0 and \
                    not (len(block.getparent().xpath("./div[2]")) > 0 and len(block.getparent().xpath("./div[2]")[0].cssselect("div.video2")) > 0):
                result = self.extract_search_result(block)
                markup.add(result)
            elif len(block.xpath("./div[1]/h2/a")) > 0 and len(block.xpath("./div[2]/div[@class='gallery']")) > 0:
                result = self.extract_wizard_image(block)
                markup.add(result)
            elif len(block.xpath("./div[1]/h2/a")) > 1:
                result = self.extract_wizard_news(block)
                markup.add(result)
        return markup

    def parse(self, raw_page):
        tree = html.document_fromstring(raw_page)
        parser_result = ParserResult()
        block_list = tree.xpath("//html/body/div[3]/div/div[2]/div/div/ul/li/div")
        for block in block_list:
            if (len(block.xpath("./div[2]/div[2]")) > 0 and block.xpath("./div[2]/div[2]")[0].text == "реклама") or \
                    (len(block.xpath("./div[1]/div[2]")) > 0 and block.xpath("./div[1]/div[2]")[0].text == "реклама"):
                result = self.parse_adv(block)
                parser_result.add(result)
                continue
            if len(block.xpath("./h2/a")) > 0 and \
                    not (len(block.getparent().xpath("./div[2]")) > 0 and len(block.getparent().xpath("./div[2]")[0].cssselect("div.video2")) > 0):
                result = self.parse_search_result(block)
                parser_result.add(result)
            elif len(block.xpath("./div[1]/h2/a")) > 0 and len(block.xpath("./div[2]/div[@class='gallery']")) > 0:
                result = self.parse_wizard_image(block)
                parser_result.add(result)
            elif len(block.xpath("./div[1]/h2/a")) > 1:
                result = self.parse_wizard_news(block)
                parser_result.add(result)
        return parser_result
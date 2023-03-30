import pathlib
from typing import Dict, TextIO

from mistletoe.ast_renderer import get_ast
from mistletoe.block_token import Document, Heading, Paragraph
from mistletoe.html_renderer import HTMLRenderer
from mistletoe.span_token import RawText

from .types import BasicSupplement, OptionSupplement, SupplementsFile


class SupplementsParser(object):
    def __init__(self):
        self.html_renderer = HTMLRenderer()
        self.__reset()

    def __reset(self):
        self.__finish = None
        self.__paragraphs = []
        self.__sub_section_title = None
        self.__option_name = None
        self.__option_description = None
        self.__parsing_options = False
        self.__current_option_value = None
        self.__supplements = []
        self.options = {}
        self.details = []
        self.properties = []

    def __get_simple_text(self, heading: Heading) -> str:
        if len(heading.children) != 1:
            raise Exception(
                f"Expected heading to have one line of simple text but there were {len(heading.children)} sub-elements"
            )
        text_child = heading.children[0]
        if not isinstance(text_child, RawText):
            raise Exception(
                f"Expected heading to contain simple raw text butit was {type(text_child)}"
            )
        return text_child.content

    def __add_options(self):
        pass

    def __add_properties(self):
        self.properties = self.__supplements

    def __add_details(self):
        self.details = self.__supplements

    def __finish_last_task(self):
        if self.__finish is not None:
            self.__finish()
        self.__finish = None
        self.__parsing_options = False
        self.__supplements = []

    def __finish_option(self):
        if self.__option_name is None:
            return
        self.options[self.__option_name.lower()] = OptionSupplement(
            self.__option_description, self.__supplements
        )
        self.__option_name = None
        self.__supplements = []

    def __finish_section(self):
        if self.__sub_section_title is None:
            if len(self.__paragraphs) != 0:
                raise Exception(
                    f"Encountered paragraphs but no L3/L4 section title starting at {self.__paragraphs[0]}"
                )
            return
        if len(self.__paragraphs) == 0:
            raise Exception(f"Sub-section {self.__sub_section_title} had no paragraphs")
        self.__supplements.append(
            BasicSupplement(self.__sub_section_title, "\n".join(self.__paragraphs))
        )
        self.__sub_section_title = None
        self.__paragraphs = []

    def __finish_last_l3(self):
        if self.__parsing_options:
            self.__finish_option()
        else:
            self.__finish_section()

    def __finish_last_l4(self):
        if self.__option_name is None:
            return
        content = "\n".join(self.__paragraphs)
        if self.__current_option_value is None:
            self.__option_description = content
        else:
            self.__supplements.append(
                BasicSupplement(self.__current_option_value.upper(), content)
            )
            self.__current_option_value = None
        self.__paragraphs = []

    def __parse_heading(self, heading: Heading):
        heading_title = self.__get_simple_text(heading)
        if heading.level == 2:
            self.__finish_last_l4()
            self.__finish_last_l3()
            self.__finish_last_task()
            if heading_title.lower() == "options":
                self.__parsing_options = True
                self.__finish = self.__add_options
            elif heading_title.lower() == "details":
                self.__finish = self.__add_details
            elif heading_title.lower() == "properties":
                self.__finish = self.__add_properties
            else:
                raise Exception(f"Unexpected L2 heading '{heading_title}'")
        elif heading.level == 3:
            if self.__finish is None:
                raise Exception(
                    f"L3 heading {heading_title} with no L2 heading preceding it"
                )
            self.__finish_last_l4()
            self.__finish_last_l3()
            if self.__parsing_options:
                self.__option_name = heading_title
            else:
                self.__sub_section_title = heading_title
        elif heading.level == 4:
            if not self.__parsing_options:
                raise Exception(
                    f"L4 heading {heading_title} encountered but we are not currently parsing options"
                )
            self.__finish_last_l4()
            self.__current_option_value = heading_title

    def __parse_paragraph(self, paragraph: Paragraph):
        self.__paragraphs.append(self.html_renderer.render_paragraph(paragraph))

    def __parse_child(self, child):
        if isinstance(child, Heading):
            self.__parse_heading(child)
        elif isinstance(child, Paragraph):
            self.__parse_paragraph(child)
        else:
            raise Exception(
                f"Unrecognized top-level element type in supplements file {type(child)}"
            )

    def parse_supplements_doc(self, f: TextIO) -> SupplementsFile:
        self.__reset()
        doc = Document(f)

        if len(doc.children) == 0:
            raise Exception(
                "Supplements document appears to be empty.  It should at least have a title"
            )

        title_section = doc.children[0]
        if not isinstance(title_section, Heading) or title_section.level != 1:
            raise Exception(
                "First element in a supplements doc should be a level 1 heading with the name of the function"
            )

        function_name = self.__get_simple_text(title_section).lower()
        for child in doc.children[1:]:
            self.__parse_child(child)

        self.__finish_last_l4()
        self.__finish_last_l3()
        self.__finish_last_task()

        return SupplementsFile(
            function_name, self.options, self.details, self.properties
        )


def load_supplements(supplements_dir: str) -> Dict[str, SupplementsFile]:
    supplements = {}
    parser = SupplementsParser()
    for sup_path in pathlib.Path(supplements_dir).rglob("*.md"):
        with open(sup_path, "r") as sup_f:
            sup = parser.parse_supplements_doc(sup_f)
            supplements[sup.function.lower()] = sup
    return supplements

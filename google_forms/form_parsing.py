"""Module that can help you with scraping data from google forms."""

from __future__ import annotations

import json
import typing
from dataclasses import dataclass, field
import bs4

import requests
from bs4 import BeautifulSoup

from . import questions_module
from .exceptions import ElementNotFoundException


@dataclass()
class Section:
    section_title: str | None
    section_description: str | None
    section_index: int


@dataclass()
class Form:
    """Information about a form (google forms).

    Atributes:
        questions: list of questions from this form, list of instances of class Question
            (or any class inheriting from Question class)
        form_name: name of this form, string
        form_description: descriptipn of this form, string or None
        question_count: how many questions are in this form
        cookies: cookies that were set after downloading the form page, string or None
        fbzx: fbzx value, string or None
    """

    form_id: str
    questions: list[questions_module.Question] = field(repr=False)
    form_name: str
    form_description: str | None
    section_history: str
    section_index_to_section_data: dict[int, Section] = field(repr=False)

    question_count: int = field(init=False)

    cookies: str | None = field(default=None, repr=False)
    fbzx: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        self.question_count = len(self.questions)

    def prepare_partial_response(self) -> list:
        return [[], None, self.fbzx]


def process_multiple_choice_question(
    question: list, section_index: int
) -> questions_module.MultipleChoiceQuestion:
    """
    This function is used for processing multiple choice questions

    Args:
        question: data about question, from data params of the div atribute, list

    Returns:
        instance of MultipleChoiceQuestion class
    """
    answers = [answ[0] for answ in question[0][4][0][1]]
    request_data_key = question[0][4][0][0]

    return questions_module.MultipleChoiceQuestion(
        question[0][1],
        question[0][0],
        section_index,
        question[0][2],
        answers,
        request_data_key,
    )


def process_text_question(
    question: list, section_index: int
) -> questions_module.TextAnswerQuestion:
    """
    This function is used for text questions (paragraph or short answer)

    Args:
        question: data about question, from data params of the div atribute, list

    Returns:
        instance of TextAnswerQuestion class
    """
    request_data_key = question[0][4][0][0]

    return questions_module.TextAnswerQuestion(
        question[0][1], question[0][0], section_index, question[0][2], request_data_key
    )


def process_checkboxes_question(
    question: list, section_index: int
) -> questions_module.CheckboxesQuestion:
    """
    This function is used for checkboxes questions

    Args:
        question: data about question, from data params of the div atribute, list

    Returns:
        instance of CheckboxesQuestion class
    """
    requests_data_key = question[0][4][0][0]

    answers = [answ[0] for answ in question[0][4][0][1]]

    return questions_module.CheckboxesQuestion(
        question[0][1],
        question[0][0],
        section_index,
        question[0][2],
        requests_data_key,
        answers,
    )


def process_dropdown_question(
    question: list, section_index: int
) -> questions_module.DropdownQuestion:
    """
    This function is used for processing dropdown questions

    Args:
        question: data about question, from data params of the div atribute, list

    Returns:
        instance of DropdownQuestion class
    """
    answers = [answ[0] for answ in question[0][4][0][1]]
    request_data_key = question[0][4][0][0]

    return questions_module.DropdownQuestion(
        question[0][1],
        question[0][0],
        section_index,
        question[0][2],
        answers,
        request_data_key,
    )


def process_linear_scale_question(
    question: list, section_index: int
) -> questions_module.LinearScaleQuestion:
    """
    This function is used for processing linear scale questions

    Args:
        question: data about question, from data params of the div atribute, list

    Returns:
        instance of LinearScaleQuestion class
    """
    possible_answers = [element[0] for element in question[0][4][0][1]]
    request_data_key = question[0][4][0][0]
    labels = question[0][4][0][3]

    return questions_module.LinearScaleQuestion(
        question[0][1],
        question[0][0],
        section_index,
        question[0][2],
        request_data_key,
        possible_answers,
        labels,
    )


def process_tick_box_grid_question(
    question: list, section_index: int
) -> questions_module.GridQuestion:
    """
    This function is used for processing multiple choice grid questions and tick box grid questions

    Args:
        question: data about question, from data params of the div atribute, list

    Returns:
        instance of GridQuestion class
    """
    column_labels = [c[0] for c in question[0][4][0][1]]
    row_labels = [row_o[3][0] for row_o in question[0][4]]

    response_required = question[0][4][0][2]  # TODO add this to all parsers
    multiple_responses_per_row = question[0][4][0][11][0]
    one_response_per_column = bool(question[0][8])

    request_data_keys = [row_o[0] for row_o in question[0][4]]

    return questions_module.GridQuestion(
        question[0][1],
        question[0][0],
        section_index,
        question[0][2],
        row_labels,
        column_labels,
        response_required,
        multiple_responses_per_row,
        one_response_per_column,
        request_data_keys,
    )


def process_questions(
    questions_json: list,
    section_index: int,
    questions_out: typing.List[questions_module.Question],
) -> None:
    """
    This function will process each questions json data and create
    a question object for each one of them

    Args:
        questions_json: list of python objects. Each objects represents json data for one question
    """

    question_object: questions_module.Question

    for question in questions_json:
        question_type = question[0][3]

        if question_type == 2:  # Multiple choice question
            question_object = process_multiple_choice_question(question, section_index)

            questions_out.append(question_object)

        elif (question_type == 0) or (
            question_type == 1
        ):  # paragraph question / short answer question
            question_object = process_text_question(question, section_index)

            questions_out.append(question_object)

        elif question_type == 4:  # checkboxes question
            question_object = process_checkboxes_question(question, section_index)

            questions_out.append(question_object)

        elif question_type == 3:  # dropdown question
            question_object = process_dropdown_question(question, section_index)

            questions_out.append(question_object)

        elif question_type == 5:  # linear scale question
            question_object = process_linear_scale_question(question, section_index)

            questions_out.append(question_object)

        elif question_type == 7:  # grid questions
            question_object = process_tick_box_grid_question(question, section_index)

            questions_out.append(question_object)


def parse_question_json_data(webpage: BeautifulSoup) -> list[list]:
    question_elements = webpage.select("div[jsmodel][data-params^='%.@.']")

    questions_json = []

    for element in question_elements:
        data_params = element.attrs["data-params"].replace("%.@.", "[")

        questions_json.append(json.loads(data_params))

    return questions_json


def is_valid_question_page(bs4_form_page: BeautifulSoup) -> bool:
    buttons = bs4_form_page.select(
        "div[data-shuffle-seed] div[class]:not(div:last-child) > div[role='button']"
    )

    return len(buttons) != 0


def get_tag_from_css(bs4_form_page: BeautifulSoup, css_selector: str) -> bs4.element.Tag:
    tag = bs4_form_page.select_one(css_selector)

    if tag is None:
        raise ElementNotFoundException("The fbzx input tag was not found.")

    return tag


def get_next_section(
    form_id: str,
    history: str,
    timeout: int = 3,
    partial_response: typing.Union[list, None] = None,
) -> str:
    data = {
        "fvv": "1",
        "pageHistory": history,
        "submissionTimestamp": "-1",
        "continue": "1",
    }

    if partial_response is not None:
        data["partialResponse"] = json.dumps(partial_response)

    url = f"https://docs.google.com/forms/d/e/{form_id}/formResponse"

    response = requests.post(
        url,
        data=data,
        timeout=timeout,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"
        },
    )

    return response.text


def get_google_form(form_id: str) -> typing.Union[Form, None]:
    """
    This functions gathers information about a google form with given id

    it scrapers all supported questions, description, title and saves cookies that were recived with the response

    Args:
        form_id: id of the form you want to scrape

    Returns:
        an instance of the Form class
    """
    response = requests.get(
        f"https://docs.google.com/forms/d/e/{form_id}/viewform",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"
        },
    )

    cookies = response.headers["set-cookie"]

    bs4_form_page = BeautifulSoup(response.text, "html.parser")

    fbzx = get_tag_from_css(
        bs4_form_page,
        "input[type='hidden'][name='fbzx']"
    ).attrs["value"]

    form_name = get_tag_from_css(bs4_form_page, "meta[itemprop='name']").attrs["content"]
    form_description = bs4_form_page.select_one("meta[itemprop='description']") # TODO handle empty description

    if form_description is not None:
        form_description_string = form_description.attrs["content"]

    questions_json = parse_question_json_data(bs4_form_page)

    question_objects: list[questions_module.Question] = []

    process_questions(questions_json, 0, question_objects)

    history = get_tag_from_css(bs4_form_page, "input[name='pageHistory']").attrs["value"]

    section_index_to_section_data: typing.Dict[int, Section] = {
        0: Section(None, None, 0)
    }

    history_prev, section_index = None, 0

    while True:
        section_answers_partial: list[list] = [[]]

        for question in question_objects:
            if question.section_index != section_index:
                continue

            question.add_random_answer_partial_response(section_answers_partial)

        next_section_html = get_next_section(
            form_id, history, partial_response=section_answers_partial
        )

        bs4_form_page = BeautifulSoup(next_section_html, "html.parser")

        if not is_valid_question_page(bs4_form_page):
            break

        history = get_tag_from_css(bs4_form_page, "input[name='pageHistory']").attrs["value"]

        if history == history_prev:
            raise Exception(  # FIXME
                "Got the same section page in two iterations, somehing went wrong"
            )

        history_prev = history

        section_index = int(history.split(",")[-1])

        section_info_div = bs4_form_page.select_one(
            "div[role='list'] > div[role='listitem']"
        )

        if not section_info_div:
            break

        section_title = section_info_div.select_one("div[jsname] > div > div")

        section_description_tag = section_info_div.select_one(
            "div:last-child" if section_title is None else "div:nth-child(2)"
        )

        if section_title is not None:
            section_title_string = section_title.text

        if section_description_tag is not None:
            section_description_string = section_description_tag.text

        questions_json = parse_question_json_data(bs4_form_page)

        process_questions(questions_json, section_index, question_objects)

        section_index_to_section_data[section_index] = Section(
            section_title_string, section_description_string, section_index
        )

    return Form(
        form_id,
        question_objects,
        form_name,
        form_description_string,
        history,
        section_index_to_section_data,
        cookies=cookies,
        fbzx=fbzx,
    )

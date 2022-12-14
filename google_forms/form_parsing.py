"""
This module can help you with scraping data from google forms (questions, title, description)
"""
from bs4 import BeautifulSoup
import requests
import json
from . import questions_module
import typing
from dataclasses import dataclass, field


@dataclass()
class Form():
    """
    This class stores information about a form (google forms)

    Atributes:
        questions: list of questions from this form, list of instances of class Question (or any class inheriting from Question class)
        form_name: name of this form, string
        form_description: descriptipn of this form, string or None
        question_count: how many questions are in this form
        cookies: cookies that were set after downloading the form page, string or None
        fbzx: fbzx value, string or None
    """
    form_id: str
    questions: list[typing.Type[questions_module.Question]] = field(repr=False)
    form_name: str
    form_description: typing.Union[str, None]
    question_count: int = field(init=False)
    cookies: str = field(default=None, repr=False)
    fbzx: str = field(default=None, repr=False)

    def __post_init__(self) -> None:
        self.question_count = len(self.questions)


def process_multiple_choice_question(question: list) -> questions_module.MultipleChoiceQuestion:
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
        question[0][1], question[0][0], answers, request_data_key
    )


def process_text_question(question: list) -> questions_module.TextAnswerQuestion:
    """
    This function is used for text questions (paragraph or short answer)

    Args:
        question: data about question, from data params of the div atribute, list

    Returns:
        instance of TextAnswerQuestion class
    """
    request_data_key = question[0][4][0][0]

    return questions_module.TextAnswerQuestion(
        question[0][1], question[0][0], request_data_key
    )


def get_google_form(form_id: str) -> Form:
    """
    This functions gathers information about a google form with given id

    it scrapers all supported questions, description, title and saves cookies that were recived with the response

    Args:
        form_id: id of the form you want to scraper

    Returns:
        an instance of the Form class
    """
    response = requests.get(f"https://docs.google.com/forms/d/e/{form_id}/viewform?usp=sf_link")

    cookies = response.headers["set-cookie"]

    bs4_form_page = BeautifulSoup(
        response.text,
        "html.parser"
    )

    fbzx = bs4_form_page.select_one("input[type='hidden'][name='fbzx']")

    if fbzx is None:
        return None

    fbzx = fbzx.attrs["value"]

    form_name = bs4_form_page.select_one("meta[itemprop='name']").attrs["content"]
    form_description = bs4_form_page.select_one("meta[itemprop='description']")

    if form_description is not None:
        form_description = form_description.attrs["content"]

    question_elements = bs4_form_page.select("div[jsmodel][data-params^='%.@.']")

    questions_json = []

    for element in question_elements:
        data_params = element.attrs["data-params"].replace("%.@.", "[")

        questions_json.append(json.loads(data_params))

    question_objects: list[typing.Type[questions_module.Question]] = []

    for question in questions_json:
        question_type = question[0][3]

        if question_type == 2:  # Multiple choice question
            question_object = process_multiple_choice_question(question)

            question_objects.append(question_object)

        elif (question_type == 0) or (question_type == 1):  # paragraph question / short answer question
            question_object = process_text_question(question)

            question_objects.append(question_object)

    return Form(form_id, question_objects, form_name, form_description, cookies=cookies, fbzx=fbzx)

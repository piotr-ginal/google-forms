from dataclasses import dataclass, field
from .import input_validation
import typing


@dataclass()
class Question:
    question_text: str
    question_id: str
    description: typing.Union[str, None]


@dataclass()
class MultipleChoiceQuestion(Question):
    """
    This class stores the needed information for multiple choice questions

    Atributes:
        answers: list of all possible answers as strings
        request_data_key: request key needed for adding a response to the request data
        answer_count: count of all possible answers for this question
    """
    answers: list[str] = field(repr=False)
    request_data_key: int
    answer_count: int = field(init=False)

    def __post_init__(self) -> None:
        self.answer_count = len(self.answers)

    def add_answer(self, index: int, data: dict) -> None:
        data[f"entry.{self.request_data_key}"] = self.answers[index]


@dataclass()
class TextAnswerQuestion(Question):
    """
    This class stores information about text answer
    questions (can be the short answer quesiton or the paragraph question)

    Atributes:
        request_data_key: request key needed for adding a response to the request data
    """
    request_data_key: int

    def add_answer(self, answer: str, data: dict) -> None:
        data[f"entry.{self.request_data_key}"] = answer


@dataclass()
class CheckboxesQuestion(Question):
    """
    This class stores information about Checboxes questions
    """
    request_data_key: int
    answers: list[str] = field(repr=False)
    answer_count: int = field(repr=False, init=False)

    def __post_init__(self) -> None:
        self.answer_count = len(self.answers)

    def add_answer(self, indexes: list[int], data: dict) -> None:
        key = f"entry.{self.request_data_key}"

        answers = [self.answers[index] for index in set(indexes)]

        data[key] = answers


@dataclass()
class DropdownQuestion(MultipleChoiceQuestion):
    """
    This class stores the needed information for multiple choice questions

    Atributes:
        answers: list of all possible answers as strings
        request_data_key: request key needed for adding a response to the request data
        answer_count: count of all possible answers for this question
    """
    pass


@dataclass()
class LinearScaleQuestion(Question):
    """
    This class stores the needed information for linear scale questions

    Atributes:
        answers: list of possible answers, all should be ranging from 0 or 1 to any number from 2 to 10
        labels: list containing two labels, for each end of the scale. (['start', 'end'] if not modified by the forms creator)
    """
    request_data_key: int
    answers: list[str]
    labels: list[str]

    def add_answer(self, index: int, data: dict) -> None:
        data[f"entry.{self.request_data_key}"] = self.answers[index]


@dataclass()
class GridQuestion(Question):
    """
    This class stores the needed information for tick box grid questions and multiple choice grid questions

    Atributes:
        rows: row names
        columns: column names
        response_required: if true, any of the rows can be left wihtout a response
        multiple_responses_per_row: if true the user can select more than one columns per row
        one_response_per_column: if true one column can be selected ony for one row
    """
    rows: list[str]
    columns: list[str]

    response_required: bool
    multiple_responses_per_row: bool
    one_response_per_column: bool

    request_data_keys: list[str]

    def add_answer(self, row_index_to_answer_index: typing.Dict[int, typing.Union[int, list[int]]], data: dict) -> None:

        for row_index, column in row_index_to_answer_index.items():

            if not isinstance(column, list):
                data[f"entry.{self.request_data_keys[row_index]}"] = self.columns[column]
                continue

            selected_column_strings: list[str] = [self.columns[column_index] for column_index in set(column)]

            data[f"entry.{self.request_data_keys[row_index]}"] = selected_column_strings

    def check_answer(self, row_index_to_answer_index: typing.Dict[int, typing.Union[int, list[int]]]) -> bool:
        """
        Check if the given answer is valid for this question
        """
        return input_validation.check_grid_question_input(self, row_index_to_answer_index)

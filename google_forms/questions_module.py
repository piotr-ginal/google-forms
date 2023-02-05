from dataclasses import dataclass, field


@dataclass()
class Question:
    question_text: str
    question_id: str


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

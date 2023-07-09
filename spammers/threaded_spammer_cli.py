"""
THREADED SPAMMER CLI

This script will ask you for a form id (https://docs.google.com/forms/d/e/{get your form id from here}/viewform?usp=sf_link),
an answer for each of the questions, then ask you how many responses you want to send.
"""

import concurrent.futures
import typing
from time import perf_counter

from google_forms import questions_module
from google_forms.form_parsing import Form, get_google_form
from google_forms.responding import post_response


MAX_WORKERS = 25


def _get_int_in_range(in_range: range, prompt: str = ">> ") -> int:
    while True:
        from_user = input(prompt)

        if not from_user.isdigit():
            continue

        if int(from_user) not in in_range:
            continue

        break

    return int(from_user)


def _get_answer_single_choice(
        question: typing.Union[questions_module.DropdownQuestion, questions_module.MultipleChoiceQuestion],
        partial: list
) -> None:
    for index, answer in enumerate(question.answers, start=1):
        print(f"\t- {index} - {answer}")

    response = _get_int_in_range(range(1, question.answer_count + 1), "select response (digit) >> ")

    question.add_answer_partial_response(response - 1, partial)


def _get_answer_text_question(
    question: questions_module.TextAnswerQuestion,
    partial: list
) -> None:
    answer = input("input text answer >> ")

    question.add_answer_partial_response(answer, partial)


def _get_answer_checkboxes_question(
    question: questions_module.CheckboxesQuestion,
    partial: list
) -> None:
    for index, answer in enumerate(question.answers, start=1):
        print(f"\t- {index} - {answer}")

    response, responses = 1, set()

    while 1:
        response = _get_int_in_range(range(0, question.answer_count + 1), "select response (one digit, type 0 to break) >> ")

        if not response:
            break

        responses.add(response - 1)

    question.add_answer_partial_response(list(responses), partial)


def get_answers(form: Form, partial: list) -> None:
    for index, question in enumerate(form.questions):
        print(f"{index} - {question.question_id} - {question.question_text}")
        if isinstance(question, (questions_module.DropdownQuestion, questions_module.MultipleChoiceQuestion)):
            _get_answer_single_choice(question, partial)

        elif isinstance(question, questions_module.TextAnswerQuestion):
            _get_answer_text_question(question, partial)

        elif isinstance(question, questions_module.CheckboxesQuestion):
            _get_answer_checkboxes_question(question, partial)

        else:
            print("this type of question is not yet supported")
            exit()


def post_response_retries(form: Form, partial: list, timeout: int = 3, retries: int = 3) -> bool:
    status_code = None

    for retry in range(retries):
        try:
            status_code = post_response(form, partial, timeout=timeout)

        except Exception as e:
            continue

        if status_code == 200:
            return True

    return False


def post_form_response_threaded(form: Form, partial: list, response_count: int, timeout: int = 3, retries: int = 3, workers: int = 10) -> None:
    results = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:

        futures = [
            executor.submit(post_response_retries, form, partial, timeout, retries) for _ in range(response_count)
        ]

        for future in concurrent.futures.as_completed(futures):
            result = future.result()

            if result not in results:
                results[result] = 0

            results[result] += 1

    print("failed: {}, succedeed: {}".format(results.get(False, 0), results.get(True, 0)))


def main():
    form = get_google_form(input("form id >> "))

    if form is None:
        print("something went wrong (check your form id, eg. 1AFEpGLSd4wrKbTMpGEPwtX3Lvk_vnWv3KuUAzjQgY9UxK6A-PQae0zw)")
        exit()

    partial = form.prepare_partial_response()

    get_answers(form, partial)

    start_time = perf_counter()

    post_form_response_threaded(
        form,
        partial,
        _get_int_in_range(range(1, 2000), "how many responses? >> "),
        workers=MAX_WORKERS
    )

    print(f"{round(perf_counter() - start_time, 2)}s")


if __name__ == "__main__":
    main()

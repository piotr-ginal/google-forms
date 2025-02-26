"""THREADED SPAMMER CLI.

This script will ask you for a form id an answer for each of the questions,
then ask you how many responses you want to send.

(https://docs.google.com/forms/d/e/{get your form id from here}/viewform?usp=sf_link)

"""

import concurrent.futures
import sys
import typing
from time import perf_counter

import click

from google_forms_toolkit import questions_module
from google_forms_toolkit.form_parsing import Form, get_google_form
from google_forms_toolkit.responding import post_response

MAX_WORKERS: int = 25
OK_STATUS_CODES: tuple[int, ...] = (200,)
MAX_RESPONSES_COUNT: int = 2000
DEFAULT_RESPONSES_COUNT: int = 1


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
        partial: list,
) -> None:
    for index, answer in enumerate(question.answers, start=1):
        sys.stdout.write(f"\t- {index} - {answer}\n")

    response = _get_int_in_range(range(1, question.answer_count + 1), "select response (digit) >> ")

    question.add_answer_partial_response(response - 1, partial)


def _get_answer_text_question(
    question: questions_module.TextAnswerQuestion,
    partial: list,
) -> None:
    answer = input("input text answer >> ")

    question.add_answer_partial_response(answer, partial)


def _get_answer_checkboxes_question(
    question: questions_module.CheckboxesQuestion,
    partial: list,
) -> None:
    for index, answer in enumerate(question.answers, start=1):
        sys.stdout.write(f"\t- {index} - {answer}\n")

    response, responses = 1, set()

    while 1:
        response = _get_int_in_range(
            range(question.answer_count + 1),
            "select response (one digit, type 0 to break) >> ",
        )

        if not response:
            break

        responses.add(response - 1)

    question.add_answer_partial_response(list(responses), partial)


def get_answers(form: Form, partial: list, *, get_random: bool = False) -> None:
    for index, question in enumerate(form.questions):
        if get_random:
            question.add_random_answer_partial_response(partial)
            continue
        sys.stdout.write(f"{index} - {question.question_id} - {question.question_text}\n")
        if isinstance(question, (questions_module.DropdownQuestion, questions_module.MultipleChoiceQuestion)):
            _get_answer_single_choice(question, partial)

        elif isinstance(question, questions_module.TextAnswerQuestion):
            _get_answer_text_question(question, partial)

        elif isinstance(question, questions_module.CheckboxesQuestion):
            _get_answer_checkboxes_question(question, partial)

        else:
            sys.stderr.write("this type of question is not yet supported")
            sys.exit(1)


def post_response_retries(form: Form, partial: list, timeout: int = 3, retries: int = 3) -> bool:
    status_code = None

    for _retry in range(retries):
        try:
            status_code = post_response(form, partial, timeout=timeout)

        except Exception:  # noqa: BLE001, S112
            continue

        if status_code in OK_STATUS_CODES:
            return True

    return False


def post_form_response_threaded(form: Form,  # noqa: PLR0913, PLR0917
    partial: list,
    response_count: int,
    timeout: int = 3,
    retries: int = 3,
    workers: int = 10,
) -> None:
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

    sys.stdout.write(f"failed: {results.get(False, 0)}, succedeed: {results.get(True, 0)}\n")


@click.command()
@click.argument("form_id", type=str)
@click.option(
    "--random",
    is_flag=True,
    help="Use random answers for the form.",
)
@click.option(
    "--responses",
    type=int,
    default=DEFAULT_RESPONSES_COUNT,
    show_default=True,
    help="Number of responses to submit.",
)
@click.option(
    "--workers",
    type=int,
    default=MAX_WORKERS,
    show_default=True,
    help="Number of worker threads to use.",
)
def main(form_id: str, random: bool, responses: int, workers: int) -> None:  # noqa: FBT001
    """Automate responses to Google Forms.

    FORM_ID: The ID of the Google Form to interact with.
    """
    if responses < 1 or responses > MAX_RESPONSES_COUNT:
        click.echo("Error: Number of responses must be between 1 and 2000.", err=True)
        sys.exit(1)

    form = get_google_form(form_id)
    if form is None:
        click.echo("Error: Could not fetch the Google Form. Check the form ID.", err=True)
        sys.exit(1)

    partial = form.prepare_partial_response()

    get_answers(form, partial, get_random=random)

    click.echo(f"Submitting {responses} responses...")
    start_time = perf_counter()
    post_form_response_threaded(
        form,
        partial,
        responses,
        workers=workers,
    )
    end_time = perf_counter()

    click.echo(f"Finished in {end_time - start_time:.2f} seconds.")


if __name__ == "__main__":
    main()

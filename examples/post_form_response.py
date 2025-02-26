"""Send one response to a form with one multiple choice question."""


from google_forms_toolkit.form_parsing import get_google_form
from google_forms_toolkit.responding import post_response

FORM_ID = "FORM ID"


def main() -> None:
    form = get_google_form(FORM_ID)

    if form is None:
        return

    partial_response: list[list] = [[]]

    form.questions[0].add_answer_partial_response(
        answer_index=0,
        partial=partial_response,
    )

    post_response(
        form,
        partial_response,
        timeout=4,
    )


if __name__ == "__main__":
    main()

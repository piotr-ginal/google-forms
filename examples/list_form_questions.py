"""This scripts will list all questions from given form and print out their representation."""

from google_forms_toolkit.form_parsing import get_google_form


def main() -> None:
    form_id = "form_id"  # eg. 1AFEpGLSd4wrKbTMpGEPwtX3Lvk_vnWv3KuUAzjQgY9UxK6A-PQae0zw

    form = get_google_form(form_id)

    for question in form.questions:

        if "answers" not in question.__annotations__:
            continue

        for _index, _answer in enumerate(question.answers, start=1):
            pass


if __name__ == "__main__":
    main()

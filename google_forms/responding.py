import requests
import json
from .form_parsing import Form


def post_response(form: Form, partial_response: list, timeout: int = 3) -> int:
    """
    Responds to the given form with given data

    Args:
        form: instance of the Form class
        partial_response: list containing responses for every form question the user wants to answer.
        Can be generated with prepare_partial_response Form method. The answers can be added using the
        add_answer_partial_response method (any question object).
    """

    data = {
        "partialResponse": json.dumps(partial_response),
        "pageHistory": form.section_history
    }

    url = f"https://docs.google.com/forms/d/e/{form.form_id}/formResponse"
    referer = f"https://docs.google.com/forms/d/e/{form.form_id}/viewform?fbzx={form.fbzx}"

    response = requests.post(
        url, data=data, headers={"Cookie": form.cookies, "Referer": referer}, timeout=timeout
    )

    return response.status_code

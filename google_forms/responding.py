import requests


def post_response(cookies: str, form_id: str, data: dict, fbzx: str, timeout: int = 3) -> None:
    """
    Responds to the given form with given data, using given cookies and fbzx

    Args:
        cookies: cookies that were set when accesng the form page (as a string)
        form_id: form id you got from the url
        data: request data as a dictionary
        fbzx: fbzx value you got from the form page
    """
    url = f"https://docs.google.com/forms/d/e/{form_id}/formResponse"
    referer = f"https://docs.google.com/forms/d/e/{form_id}/viewform?fbzx={fbzx}"

    response = requests.post(
        url, data=data, headers={"Cookie": cookies, "Referer": referer}, timeout=timeout
    )

    return response.status_code

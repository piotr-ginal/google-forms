from __future__ import annotations

import typing


def check_grid_question_input(question, row_index_to_answer_index: dict[int, typing.Union[int, list[int]]]) -> bool:  # noqa: ANN001, UP007
    """Check if the provided answer is valid for the given question.

    - if the user provided a response for each of the rows (if the given question requires it)
    - if the user selected more than one answer for a given row (when its not allowed)
    - if the user selected a column more than once (when its not allowed).

    Args:
        question: the question you want to check your answer for
        row_index_to_answer_index: row index mapped to a selected column index or a list of column indexes

    Returns:
        True if question is valid False otherwise

    """
    # if all rows need to have a value assigned check if its the case
    if question.response_required and len(row_index_to_answer_index.keys()) < len(question.rows):
        return False

    columns_used = set()

    for column_info in row_index_to_answer_index.values():
        if isinstance(column_info, list):
            # check if the user selected more than one answer when its not allowe
            if (not question.multiple_responses_per_row) and (len(column_info) > 1):
                return False

            # check if user selected a column twice when its not allowed
            if not question.one_response_per_column:
                continue

            for column in set(column_info):
                if column in columns_used:
                    return False

                columns_used.add(column)

        else:
            # check if user selected a column twice when its not allowed
            if question.one_response_per_column and column_info in columns_used:
                return False

            columns_used.add(column_info)

    return True

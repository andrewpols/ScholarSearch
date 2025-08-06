"""CSC111 Winter 2025 Project 2: Miscellaneous Utility Functions

This file contains utility functions that are used in the project.
"""

from flask import session

STOP_WORDS = ("the", "and", "of", "is", "about", "for", "paper", "study", "research", "result",
              "method", "approach", "show", "propose", "based", "analysis")


def is_partial_match(s1: str, s2: str, threshold: float = 0.9) -> bool:
    """
    Return whether s1 partially matches s2 based on the threshold comparison of the ratio of their common words.

    >>> is_partial_match("This is a test", "This is a test", 0.9)
    True
    >>> is_partial_match("My name is John", "I go to school", 0.7)
    False
    """
    comp1 = s1.lower().split()
    comp2 = s2.lower().split()
    common_words = [word for word in comp1 if word in comp2]
    match_ratio = 0
    if comp1:
        match_ratio = len(common_words) / len(comp1)
    return match_ratio >= threshold


def calculate_weight(x: int) -> int:
    """
    Return a weight based on the number of citations.

    >>> calculate_weight(60)
    16
    >>> calculate_weight(5)
    5
    """
    if x > 50:
        return 16
    elif x > 25:
        return 13
    elif x > 10:
        return 10
    elif x > 5:
        return 7
    elif x > 2:
        return 5
    else:
        return 3


def tokenize(text: str, stop_strs: tuple[str] = STOP_WORDS) -> list[str]:
    """
    Return a list of tokens from the given text.

    >>> tokenize("This is a test")
    ['this', 'a', 'test']
    >>> tokenize("An analysis on antibodies and proteins")
    ['an', 'on', 'antibodies', 'proteins']
    """
    return [word.lower() for word in text.split() if word.isalpha() and word.lower() not in stop_strs]


def save_search_history(search_history: list[str]) -> None:
    """Save the user's search history to the session."""
    session['search_history'] = search_history


def load_search_history() -> list[str]:
    """Load the user's search history from the session."""
    return session.get('search_history', [])


def add_to_search_history(query: str) -> None:
    """Add a search query to the user's session-based search history."""
    search_history = load_search_history()
    if query not in search_history[-3:]:
        search_history.append(query)
        if len(search_history) > 3:
            search_history.pop(0)

        save_search_history(search_history)


if __name__ == "__main__":
    pass
    # # Optional: Uncomment code for testing purposes
    # import doctest
    # doctest.testmod()
    #
    # import python_ta
    #
    # python_ta.check_all(config={
    #     'extra-imports': [],  # the names (strs) of imported modules
    #     'allowed-io': [],  # the names (strs) of functions that call print/open/input
    #     'max-line-length': 120
    # })

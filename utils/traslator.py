from functools import wraps

from googletrans import Translator

translator = Translator()

def translater(func):
    """
    A decorator that translates the output of a function using the Google Translate API.

    Args:
        func: The function to be decorated.

    Returns:
        The traslated output of the func.

    Example:
        ```python
        @translater
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        print(greet("John"))  # Output: สวัสดีครับ John!
        ```
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return translator.translate(func(*args, **kwargs), dest="th").text

    return wrapper
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
from urllib.parse import urlparse

# from markitdown import MarkItDown

from typing import Literal

_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=150,
    length_function=len,
    is_separator_regex=False,
)

# _markitdown = MarkItDown()


def text_splitter(text: str) -> list[str]:
    texts = _text_splitter.create_documents([text])

    return [text.page_content for text in texts]


def determine_type(
    unknown_type_of_string: str,
) -> Literal["url", "filepath", "filename", "plain_string"]:
    """
    Determines if the input string is a plain string, filename, filepath, or URL.

    Args:
        unknown_type_of_string (str): Input string to analyze

    Returns:
        str: Type of the input ('url', 'filepath', 'filename', or 'plain_string')
    """

    # Check if string is empty or None
    if not unknown_type_of_string:
        return "plain_string"

    # URL pattern check
    # Checks for common protocol prefixes and domain patterns
    url_pattern = r"^(https?:\/\/)?([\w\d\-]+\.)+[\w\d\-]+(\/[\w\d\-\.\/]*)?$"
    if re.match(url_pattern, unknown_type_of_string):
        # Additional validation using urlparse
        parsed = urlparse(unknown_type_of_string)
        if parsed.netloc or parsed.scheme:
            return "url"

    # Filepath pattern check
    # Matches both Windows and Unix-style paths
    filepath_pattern = r"^(([A-Za-z]:)?[\\/]|~[\\/]|\.\.[\\/]|\.[\\/]|[\\/])([^\\/\0]+([\\/])?)*$"
    if re.match(filepath_pattern, unknown_type_of_string):
        return "filepath"

    # Filename pattern check
    # Checks for valid filename characters and common extensions
    filename_pattern = r"^[\w\-. ]+\.[A-Za-z0-9]+$"
    if re.match(filename_pattern, unknown_type_of_string):
        return "filename"

    # If none of the above patterns match, it's a plain string
    return "plain_string"


def source_to_markdown(source: str):
    """
    Light wrapper around Microsoft's Markitdown
    """
    # return _markitdown.convert(source).text_content
    return ""

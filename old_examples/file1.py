from swiftagent import SwiftAgent

import asyncio
import subprocess
from typing import List
import os
from markitdown import MarkItDown

agent = SwiftAgent(name="file1_agent", fresh_install=True)


@agent.action(
    name="search_files",
    strict=False,
    params={
        "phrase": "Phrase to search",
        "limit": "Number of files/documents to retrieve",
    },
    description="Function that gives a list of files that are similar to the phrase on the computer. Returns a list of strings representing the filepaths.",
)
def search_files(phrase: str, limit: int = 10) -> List[str]:
    """
    Search for readable document files related to a phrase using macOS mdfind command,
    excluding development and cache directories.

    Args:
        phrase (str): The search phrase to look for
        limit (int): Maximum number of results to return (default: 10)

    Returns:
        List[str]: List of document file paths matching the search criteria
    """
    # Define readable document extensions
    READABLE_EXTENSIONS = {
        # Text documents
        ".txt",
        ".rtf",
        ".md",
        # Office documents
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".odt",
        ".ods",
        ".odp",  # OpenOffice/LibreOffice
        # PDF documents
        ".pdf",
        # Common formats
        ".csv",
        # Apple formats
        ".pages",
        ".numbers",
        ".key",
    }

    # Define patterns for directories to exclude
    EXCLUDED_PATTERNS = {
        # Development directories
        "node_modules",
        "venv",
        ".venv",
        "env",
        ".env",
        "virtualenv",
        ".git",
        ".svn",
        ".hg",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "build",
        "dist",
        # Cache directories
        "Library/Caches",
        "Library/Application Support",
        ".cache",
        # Package managers
        "pip-wheel-metadata",
        ".npm",
        "bower_components",
        # IDE directories
        ".idea",
        ".vscode",
        ".vs",
        # Temp directories
        "tmp",
        "temp",
        # Other common exclusions
        ".Trash",
        "site-packages",
        "Library",  # This will catch all Library folders
        "/Library/",  # System library
        "~/Library/",  # User library
    }

    def should_exclude(file_path):
        """Check if the file path contains any excluded patterns."""
        normalized_path = os.path.normpath(file_path)
        path_parts = normalized_path.split(os.sep)

        return any(excluded in path_parts for excluded in EXCLUDED_PATTERNS)

    try:
        # First get all results for the phrase
        cmd = ["mdfind", "-0", phrase]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Split results and filter by extension and excluded directories
        files = [
            f
            for f in result.stdout.split("\0")
            if f
            and os.path.splitext(f)[1].lower() in READABLE_EXTENSIONS
            and not should_exclude(f)
        ]

        # Verify files exist and are readable
        verified_files = []
        for file_path in files[:limit]:
            try:
                if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
                    verified_files.append(file_path)
            except (OSError, IOError):
                continue

        return verified_files

    except subprocess.CalledProcessError as e:
        print(f"Error executing mdfind: {e}")
        raise
    except FileNotFoundError:
        print(
            "mdfind command not found. This function only works on macOS systems."
        )
        raise


@agent.action(
    name="read_files",
    params={"filenames": "list of filenames to read contents of"},
    description="Function that returns the text content of given files",
)
def read_files(filenames: list[str]):
    md = MarkItDown()

    return "\n".join(
        [f"# {filename} \n {md.convert(filename)} \n" for filename in filenames]
    )


async def main():
    await agent.run(
        task="what percentage of openminder labs shares does leanne have now? search my computer for the info"
    )


asyncio.run(main())

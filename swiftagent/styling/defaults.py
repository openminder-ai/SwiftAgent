from rich.theme import Theme

suite_cli_default = Theme(
    {
        "info": "bold cyan",  # Brighter cyan for clarity
        "url": "bold bright_blue on black",  # Blue on black for contrast
        "success": "bold green",  # Regular green (bright can be too intense)
        "code": "bold yellow",  # Yellow stands out without blinding
        "optional": "dim magenta",  # Soft magenta for subtlety
    }
)

client_cli_default = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "red bold",
        "success": "green",
        "ws": "blue bold",
    }
)

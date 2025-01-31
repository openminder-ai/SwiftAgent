from rich.console import Console
import time

console = Console()


# "point" - looks like a thinking/processing dot
def agent_thinking():
    with console.status(
        "[bold blue]Agent processing...", spinner="point"
    ) as status:
        time.sleep(5)


# "dots9" - smooth circular motion that suggests "thinking"
def agent_thinking2():
    with console.status(
        "[bold blue]Agent processing...", spinner="dots9"
    ) as status:
        time.sleep(5)


# "bouncingBar" - looks like a scanning/processing indicator
def agent_thinking3():
    with console.status(
        "[bold blue]Agent processing...", spinner="bouncingBar"
    ) as status:
        time.sleep(5)


# "aesthetic" - modern dots that suggest neural processing
def agent_thinking4():
    with console.status(
        "[bold blue]Agent processing...", spinner="aesthetic"
    ) as status:
        time.sleep(5)


agent_thinking4()

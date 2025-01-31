from rich.console import Console
from rich.live import Live
from rich.table import Table
from time import sleep
from collections import OrderedDict
from typing import Dict

console = Console()


def create_table(agents_status: Dict[str, bool]):
    table = Table()
    table.add_column("Agent")
    table.add_column("Status")

    for agent, is_registered in agents_status.items():
        status = "[green][✓] Registered" if is_registered else "[ ] Pending"
        table.add_row(agent, status)

    return table


def register_agents():
    # Using OrderedDict to maintain insertion order
    agents_status = OrderedDict()

    with Live(create_table(agents_status), refresh_per_second=4) as live:
        # Simulate receiving new agents
        while True:
            try:
                # You can replace this with your actual input method
                agent_name = input("Enter agent name (or 'q' to quit): ")
                if agent_name.lower() == "q":
                    break

                # Add new agent with pending status
                agents_status[agent_name] = False
                live.update(create_table(agents_status))

                # Simulate registration process
                sleep(1)
                agents_status[agent_name] = True
                live.update(create_table(agents_status))

            except KeyboardInterrupt:
                break


console.print("[bold blue]Starting Dynamic Agent Registration Process...[/]")
register_agents()
console.print("[bold green]Registration Complete![/]")

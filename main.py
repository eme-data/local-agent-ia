#!/usr/bin/env python3
"""Point d'entrée CLI de Autobot."""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from src.agent import Agent
from src.database import Database
from src.tools import init_tools

console = Console()


def main():
    console.print(
        Panel(
            "[bold]Autobot[/bold]\n"
            "Tape ton message pour discuter. Commandes spéciales :\n"
            "  [cyan]/quit[/cyan]  — Quitter\n"
            "  [cyan]/reset[/cyan] — Nouvelle conversation",
            title="🤖 Bienvenue",
            border_style="blue",
        )
    )

    db = Database()
    init_tools(db=db)

    try:
        agent = Agent(db=db)
    except ValueError as e:
        console.print(f"[red]Erreur: {e}[/red]")
        return

    while True:
        try:
            user_input = console.input("\n[bold green]Toi >[/bold green] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Au revoir ![/dim]")
            break

        if not user_input:
            continue
        if user_input == "/quit":
            console.print("[dim]Au revoir ![/dim]")
            break
        if user_input == "/reset":
            agent.reset()
            console.print("[yellow]Conversation réinitialisée.[/yellow]")
            continue

        with console.status("[bold blue]Réflexion en cours...[/bold blue]"):
            try:
                response = agent.chat(user_input)
            except Exception as e:
                console.print(f"[red]Erreur: {e}[/red]")
                continue

        console.print()
        console.print(Markdown(response))

    db.close()


if __name__ == "__main__":
    main()

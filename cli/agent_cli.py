"""
MCP Agent CLI - Command-line interface for agent interaction
"""

import click
import requests
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()
MCP_SERVER_URL = "http://localhost:8000"


@click.group()
def cli():
    """🤖 MCP Multi-Agent System CLI"""
    pass


@cli.command()
def list():
    """List all available agents"""
    try:
        response = requests.get(f"{MCP_SERVER_URL}/api/v1/agents")
        response.raise_for_status()
        data = response.json()
        
        table = Table(title="🤖 MCP Agents", show_header=True, header_style="bold magenta")
        table.add_column("Agent ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("Role", style="yellow")
        table.add_column("Tone", style="blue")
        
        for agent in data['agents']:
            table.add_row(
                agent['id'],
                agent['name'],
                agent['role'],
                agent['tone']
            )
        
        console.print(table)
        console.print(f"\n[bold]Total agents:[/bold] {data['total']}")
        
    except requests.exceptions.ConnectionError:
        console.print("[bold red]❌ Error: Cannot connect to MCP server[/bold red]")
        console.print("[yellow]Make sure the server is running: python server/main.py[/yellow]")
    except Exception as e:
        console.print(f"[bold red]❌ Error: {str(e)}[/bold red]")


@cli.command()
@click.argument('agent_id')
@click.argument('message')
@click.option('--session', '-s', help='Session ID for conversation continuity')
@click.option('--context', '-c', help='Context package (JSON string)')
def ask(agent_id, message, session, context):
    """Ask a question to an agent"""
    try:
        payload = {
            "agent_id": agent_id,
            "message": message
        }
        
        if session:
            payload["session_id"] = session
        
        if context:
            payload["context_package"] = json.loads(context)
        
        console.print(f"\n[bold cyan]🤔 Asking {agent_id}...[/bold cyan]\n")
        
        response = requests.post(f"{MCP_SERVER_URL}/api/v1/agent/invoke", json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Display response
        panel = Panel(
            Markdown(data['response']),
            title=f"[bold green]{data['agent_name']}[/bold green]",
            border_style="green"
        )
        console.print(panel)
        
        console.print(f"\n[dim]Session ID: {data['session_id']}[/dim]")
        
    except requests.exceptions.ConnectionError:
        console.print("[bold red]❌ Error: Cannot connect to MCP server[/bold red]")
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]❌ HTTP Error: {e.response.status_code}[/bold red]")
        console.print(f"[red]{e.response.json().get('detail', 'Unknown error')}[/red]")
    except Exception as e:
        console.print(f"[bold red]❌ Error: {str(e)}[/bold red]")


@cli.command()
@click.argument('agent_id')
def status(agent_id):
    """Get agent's current status"""
    try:
        response = requests.get(f"{MCP_SERVER_URL}/api/v1/agent/{agent_id}/status")
        response.raise_for_status()
        data = response.json()
        
        console.print(f"\n[bold cyan]📊 Status for {agent_id}[/bold cyan]\n")
        
        if 'current_status' in data['context']:
            console.print(Markdown(data['context']['current_status']))
        else:
            console.print("[yellow]No status information available[/yellow]")
        
        if 'work_log' in data['context'] and data['context']['work_log']:
            work_log = data['context']['work_log']
            console.print(f"\n[bold]Last updated:[/bold] {work_log.get('last_updated', 'N/A')}")
            console.print(f"[bold]Total sessions:[/bold] {len(work_log.get('work_sessions', []))}")
        
    except requests.exceptions.ConnectionError:
        console.print("[bold red]❌ Error: Cannot connect to MCP server[/bold red]")
    except Exception as e:
        console.print(f"[bold red]❌ Error: {str(e)}[/bold red]")


@cli.command()
@click.option('--agent', '-a', help='Filter by agent ID')
def sessions(agent):
    """List conversation sessions"""
    try:
        params = {}
        if agent:
            params['agent_id'] = agent
        
        response = requests.get(f"{MCP_SERVER_URL}/api/v1/sessions", params=params)
        response.raise_for_status()
        data = response.json()
        
        table = Table(title="💬 Conversation Sessions", show_header=True, header_style="bold magenta")
        table.add_column("Session ID", style="cyan")
        table.add_column("Agent", style="green")
        table.add_column("Created", style="yellow")
        table.add_column("Last Active", style="blue")
        
        for session in data['sessions']:
            table.add_row(
                session['session_id'][:16] + "...",
                session['agent_id'],
                session['created_at'],
                session['last_active']
            )
        
        console.print(table)
        console.print(f"\n[bold]Total sessions:[/bold] {data['total']}")
        
    except requests.exceptions.ConnectionError:
        console.print("[bold red]❌ Error: Cannot connect to MCP server[/bold red]")
    except Exception as e:
        console.print(f"[bold red]❌ Error: {str(e)}[/bold red]")


@cli.command()
@click.argument('session_id')
@click.option('--limit', '-l', default=50, help='Number of messages to show')
def history(session_id, limit):
    """Show conversation history for a session"""
    try:
        response = requests.get(
            f"{MCP_SERVER_URL}/api/v1/session/{session_id}/history",
            params={'limit': limit}
        )
        response.raise_for_status()
        data = response.json()
        
        console.print(f"\n[bold cyan]📜 History for session {session_id[:16]}...[/bold cyan]\n")
        
        for msg in data['history']:
            role = msg['role']
            content = msg['parts'][0] if msg['parts'] else ""
            
            if role == "user":
                console.print(f"[bold blue]👤 User:[/bold blue] {content}\n")
            else:
                console.print(f"[bold green]🤖 Agent:[/bold green] {content}\n")
        
        console.print(f"[dim]Total messages: {data['message_count']}[/dim]")
        
    except requests.exceptions.ConnectionError:
        console.print("[bold red]❌ Error: Cannot connect to MCP server[/bold red]")
    except Exception as e:
        console.print(f"[bold red]❌ Error: {str(e)}[/bold red]")


if __name__ == '__main__':
    cli()

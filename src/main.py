import typer
from src.cli.commands import analyze_app, export_app

__version__ = "0.1.0"

app = typer.Typer(
    name="sentiment-cli",
    help="Sentiment analysis CLI for X.com (Twitter) tweets",
)
app.add_typer(analyze_app, name="analyze")
app.add_typer(export_app, name="export")


@app.command("version")
def version() -> None:
    """Print version."""
    typer.echo(f"sentiment-cli v{__version__}")


if __name__ == "__main__":
    app()
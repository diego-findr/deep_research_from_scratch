import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme

# Define a custom theme for our application
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "agent": "bold blue",
    "decision": "bold magenta",
})

console = Console(theme=custom_theme)

def setup_logging():
    """Configure logging with Rich handler."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True, markup=True)]
    )
    
    # Suppress noisy logs from libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

def get_logger(name: str):
    """Get a logger instance."""
    return logging.getLogger(name)

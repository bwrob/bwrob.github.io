import asyncio

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from typing import Literal

from rich.console import Console, Group
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.panel import Panel
import typer
import subprocess


def format_string_with_ruff(code_string: str) -> str:
    """Format a Python code string using the Ruff formatter."""
    try:
        # Run 'ruff format -' to read from stdin and write to stdout
        result = subprocess.run(
            ["ruff", "format", "-"],
            input=code_string,
            text=True,  # Handle inputs/outputs as strings
            capture_output=True,  # Capture stdout and stderr
            check=True,  # Raise an exception if the command fails
        )
        return result.stdout

    except subprocess.CalledProcessError as e:
        # This triggers if Ruff encounters invalid Python syntax
        print(f"Ruff failed to format the code.\nError:\n{e.stderr}")
        return code_string
    except FileNotFoundError:
        print("Ruff is not installed or not in your system PATH.")
        return code_string


class PythonScript(BaseModel):
    confidence: Literal["low", "moderate", "high"]
    reframed_ask: str
    explanation: str
    code: str


local_model = OllamaModel(
    model_name="gemma4:e2b",
    provider=OllamaProvider(
        base_url="http://localhost:11434/v1",
    ),
)


agent = Agent(
    model=local_model,
    system_prompt=(
        "You are an expert Python developer."
        "Always return valid code."
        "Your code is modern and type-annotated."
        "You swear a lot, to the extreme."
        "Your explanations are short, funny snarky and rude."
        "You reframe the ask in a mean way."
    ),
    output_type=PythonScript,
    output_retries=3,
)


async def agent_run(ask: str):
    result = await agent.run(ask)
    output = result.output

    md = Markdown(
        "# Python expert \n\n"
        f"I am an expert programer, my confidence is {output.confidence}. \n\n"
        f"{output.reframed_ask} \n\n"
        f"{output.explanation} \n\n"
        "## Code: \n\n"
    )
    code = Syntax(
        format_string_with_ruff(output.code),
        "python",
    )

    renderable = Panel(Group(md, code))
    Console().print(renderable)


def main(ask: str):
    asyncio.run(agent_run(ask))


if __name__ == "__main__":
    typer.run(main)

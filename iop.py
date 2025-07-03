#!/usr/bin/env python3

from cli import main, parse_arguments  # type: ignore
from prompt import ensure_prompt_is_question  # type: ignore
from executor import check_for_markdown, check_for_issue  # type: ignore
from openrouter import read_config  # type: ignore

# Re-export names expected by downstream code/tests for compatibility
__all__ = [
    "main",
    "parse_arguments",
    "ensure_prompt_is_question",
    "check_for_markdown",
    "check_for_issue",
    "read_config",
]

if __name__ == "__main__":
    # Delegate execution to the new entrypoint implemented in cli.py
    main()

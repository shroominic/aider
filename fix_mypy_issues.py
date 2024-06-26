import subprocess
from typing import List

from aider.coders import Coder
from aider.io import InputOutput
from aider.models import Model


def get_mypy_errors(directory: str) -> List[str]:
    result = subprocess.run([".venv/bin/mypy", directory], capture_output=True, text=True)
    stdout_output = result.stdout.strip()
    errors = stdout_output.split("\n")
    return errors


def get_coder(
    model: str = "gpt-4o",
    git_dname: str = ".",
    chat_history_file: str = "history.md",
    test_cmd: str = "pytest",
) -> Coder:
    """
    Get an instance of aider to work with the given LLM `model` at `temperature`
    on the code in `git_dname`. Will store the markdown chat logs in
    the `chat_history_file`. Tells aider it can use the `test_cmd` to
    run tests after the LLM edits files.

    If `oracle_files` are provided, they are added to the aider chat automatically.
    """
    model = Model(model)
    io = InputOutput(
        yes=True,  # Say yes to every suggestion aider makes
        chat_history_file=chat_history_file,  # Log the chat here
        input_history_file="/dev/null",  # Don't log the "user input"
    )

    dump(git_dname)

    coder = Coder.create(
        main_model=model,
        io=io,
        git_dname=git_dname,
        map_tokens=2048,  # Use 2k tokens for the repo map
        stream=False,
        auto_commits=False,  # Don't bother git committing changes
        auto_test=True,  # Automatically run the test_cmd after making changes
        test_cmd=test_cmd,
        verbose=True,
    )
    coder.temperature = 0.1

    # Take at most 4 steps before giving up.
    # Usually set to 5, but this reduces API costs.
    coder.max_reflections = 4

    # Add announcement lines to the markdown chat log
    coder.show_announcements()

    # messages = coder.format_messages()
    # utils.show_messages(messages)

    return coder


def fix_issue(error: str) -> None:
    coder = get_coder()
    coder.run(error)


if __name__ == "__main__":
    directory = "aider"
    errors = get_mypy_errors(directory)
    for error in errors[1:5]:
        print("fixing:", error)
        fix_issue(error)

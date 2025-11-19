Contributing to Helldivers 2 Discord Bot
========================================

Thank you for your interest in contributing. This project is open source under the MIT License and welcomes bug fixes, improvements, and new features that keep the bot reliable and easy to self-host.


Getting Started
---------------

- Make sure you have:
  - Python 3.10 or newer
  - A MongoDB instance (local or remote)
  - A Discord application and bot token
- Clone the repository and create a virtual environment:

  ```bash
  git clone <this-repo-url>
  cd <repo-folder>
  python -m venv .venv
  .venv\Scripts\activate  # on Windows
  # or: source .venv/bin/activate  # on Linux/macOS
  pip install -r requirements.txt
  ```

- Create a `.env` file (for example by copying `.env.example`) based on the examples in `README.md` and run the bot with:

  ```bash
  python main.py
  ```


Making Changes
--------------

1. Fork the repository on your Git hosting platform.
2. Create a feature branch from `main` (for example, `feature/leaderboard-filter`).
3. Make your changes, keeping to the existing style and structure:
   - Prefer clear, descriptive names over one-letter variables.
   - Follow the patterns used in existing cogs and helpers.
   - Keep changes focused and avoid mixing unrelated refactors.
4. Add or update tests under `tests/` where it makes sense, especially for:
   - Promotion / leaderboard logic
   - New commands or flows that change behavior


Running Tests
-------------

This project uses `pytest` and `pytest-asyncio`.

- Run the full test suite:

  ```bash
  pytest
  ```

All tests should pass before you open a pull request. If you cannot get a test to pass and believe it is unrelated to your change, mention this clearly in your PR description.


Opening a Pull Request
----------------------

When you are ready to propose your changes:

- Push your feature branch to your fork.
- Open a pull request against the `main` branch.
- In the PR description, include:
  - A short summary of the change and motivation.
  - Any new environment variables, roles, or channels required.
  - Notes on database migrations or data shape changes (if any).
  - Confirmation that `pytest` passes (or details about any failing tests).

Small, focused PRs are much easier to review than large, mixed changes.


Reporting Issues and Requesting Features
----------------------------------------

If you find a bug or have a feature request, please open an issue and include:

- The behavior you expected vs. what happened.
- Steps to reproduce (commands used, screenshots if relevant).
- Relevant log output from the monitor channel or application logs.
- Your environment details (Python version, hosting platform, MongoDB type).

Security-impacting issues (for example, token leakage, privilege escalation) should be reported privately to the maintainer if possible rather than in a public issue.


Code of Conduct
---------------

Please be respectful and constructive in all interactions. Treat other contributors and server owners as collaborators. The project follows the same general expectations as the Discord Community Guidelines and developer policies.

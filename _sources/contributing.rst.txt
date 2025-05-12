====================
Contributing
====================

Thank you for considering contributing to ISEK! We're thrilled you're interested in making ISEK better. ISEK is an open-source project, and we welcome contributions of all kinds, from bug fixes to new features and documentation improvements.

Ways to Contribute
------------------

*   **Reporting Bugs:** If you find a bug, please open an issue on GitHub. Include as much detail as possible: steps to reproduce, expected behavior, actual behavior, and your environment.
*   **Suggesting Enhancements:** Have an idea for a new feature or an improvement to an existing one? Open an issue to discuss it.
*   **Code Contributions:** Fixing bugs, implementing new features, or improving existing code.
*   **Documentation:** Improving our README, adding examples, or writing more detailed documentation.
*   **Community Support:** Helping answer questions in issues or other community channels (if applicable).

Getting Started: Your First Contribution
----------------------------------------

Unsure where to begin? You can start by looking through ```good first issue``` or ```help wanted``` issues in our repository.

If you're ready to contribute code, here's how to set up ISEK for local development:

1.  **Fork the Repository:**
    Click the "Fork" button at the top right of the `ISEK GitHub page <https://github.com/your_org_or_username/isek>`_ (replace with the actual ISEK project repository URL). This creates your own copy of the project.

2.  **Clone Your Fork:**

    .. code-block:: bash

       git clone https://github.com/YOUR_GITHUB_USERNAME/isek.git
       cd isek

    Replace ``YOUR_GITHUB_USERNAME`` with your GitHub username.

3.  **Set Up a Virtual Environment:**
    We recommend using a virtual environment to manage dependencies.

    *   **Using ``venv`` (standard Python):**

        .. code-block:: bash

           python -m venv .venv
           source .venv/bin/activate  # On Windows: .venv\Scripts\activate

    *   **Using Hatch (if your project is set up with it):**
        Hatch will manage virtual environments for you.

        .. code-block:: bash

           hatch env create
           hatch shell # To activate the environment managed by Hatch

4.  **Install Dependencies:**

    *   **If using ``venv`` and you have a ``requirements-dev.txt`` or similar:**

        .. code-block:: bash

           pip install -r requirements-dev.txt # Or just requirements.txt
           pip install -e . # Install ISEK in editable mode

    *   **If using Hatch:**
        Hatch usually installs dependencies when creating the environment. If you have specific dependency groups (e.g., ``dev``, ``test``), they might be installed automatically or you can install them with:

        .. code-block:: bash

           hatch dep install dev test # Example, adjust as needed

        The project itself is usually installed in editable mode automatically by Hatch.

5.  **Install Pre-commit Hooks:**
    We use ``pre-commit`` to ensure code style and quality before committing.

    .. code-block:: bash

       pip install pre-commit # If not already installed via dev dependencies
       pre-commit install

    This will run checks automatically every time you commit. You can also run them manually:

    .. code-block:: bash

       pre-commit run --all-files

Making Changes
--------------

1.  **Create a New Branch:**
    Create a branch from the ``main`` (or ``develop``, whichever is your primary development branch) for your feature or bug fix. Use a descriptive name.

    .. code-block:: bash

       git checkout main # Or develop
       git pull upstream main # Ensure you have the latest changes from the main repository
       git checkout -b feat/your-descriptive-feature-name  # For a new feature
       # or
       git checkout -b fix/issue-number-short-description # For a bug fix

    .. note::
       The ``git pull upstream main`` command assumes you've set up ``upstream`` to point to the original ISEK repository (e.g., ``git remote add upstream https://github.com/your_org_or_username/isek.git`` - replace with the actual ISEK project repository URL).

2.  **Add Your Feature or Improvement:**
    Write your code! Make sure to:

    *   Follow the existing code style.
    *   Add tests for any new functionality or bug fixes.
    *   Update documentation if you're changing behavior or adding features.

3.  **Run Pre-commit Checks:**
    Before you commit, ensure ``pre-commit`` checks pass. If you installed the hooks, they will run automatically on ``git commit``. If they fail, address the issues and try committing again.

4.  **Run Tests:**
    Ensure all tests pass.

    *   **If using ``pytest`` directly:**

        .. code-block:: bash

           pytest

    *   **If using Hatch (assuming a ``test`` script is defined in ``pyproject.toml``):**

        .. code-block:: bash

           hatch run test
           # or for coverage
           hatch run test:cov

5.  **Commit Your Changes:**
    Use clear and concise commit messages. If your changes address a specific issue, reference it in your commit message (e.g., ``Fixes #123``).

    .. code-block:: bash

       git add .
       git commit -m "feat: Add X functionality to Y module"

6.  **Push to Your Fork:**

    .. code-block:: bash

       git push origin feat/your-descriptive-feature-name

Submitting a Pull Request (PR)
------------------------------

1.  Go to the ISEK repository on GitHub. You should see a prompt to create a Pull Request from your recently pushed branch.
2.  Click "Compare & pull request".
3.  Ensure the base repository is ``your_org_or_username/isek`` (replace with actual) and the base branch is ``main`` (or ``develop``).
4.  Provide a clear title and a detailed description for your PR:

    *   **Title:** A brief summary of the changes (e.g., "Feat: Add support for Z").
    *   **Description:** Explain the "what" and "why" of your changes. If it fixes an issue, link to it (e.g., "Closes #123"). Include any relevant context or screenshots.

5.  Click "Create pull request."

Pull Request Review Process
---------------------------

*   Once your PR is submitted, project maintainers or assigned community members will review it.
*   We may ask for changes or clarifications. Please be responsive to feedback.
*   Once the PR is approved and all checks pass, it will be merged.

We appreciate your patience during the review process!

Code Style
----------

We use tools like Black for code formatting and Ruff/Flake8 for linting, managed via ``pre-commit``. Please ensure your contributions adhere to these standards by running ``pre-commit`` before submitting your PR.

Questions?
----------

If you have questions or need help, feel free to open an issue with the ``question`` label, or reach out on our community channels (e.g., Discord, Slack - list them here if applicable).

Thank you for contributing to ISEK!
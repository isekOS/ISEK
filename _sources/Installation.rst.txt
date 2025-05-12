************
Installation
************

This guide covers how to install the ``isek`` framework.

Prerequisites
=============

*   **Python:** Isek requires **Python 3.8 or higher**. Please ensure you have a compatible Python version installed. You can check your version using:

    .. code-block:: bash

       python --version
       # or
       python3 --version

Standard Installation (Recommended)
===================================

We strongly recommend installing Isek within a Python virtual environment to manage dependencies effectively and avoid conflicts with other system packages.

1.  **(Optional but Recommended) Create and activate a virtual environment:**

    .. code-block:: bash

       # Choose a name for your environment, e.g., .venv
       python -m venv .venv

       # Activate the environment
       # On Linux/macOS:
       source .venv/bin/activate
       # On Windows (Command Prompt):
       # .venv\Scripts\activate.bat
       # On Windows (PowerShell):
       # .venv\Scripts\Activate.ps1

2.  **Install Isek using pip:**

    Once your environment is activated (or if you choose to install globally), run:

    .. code-block:: bash

       pip install isek

    This command will download and install the latest stable release of Isek from the Python Package Index (PyPI).


Known Issues & Troubleshooting
==================================

**macOS: `faiss-cpu` Error during Installation**

If you are using macOS and encounter an error related to the `faiss-cpu` package during installation (this has been observed with Python 3.9.6 but might affect other versions), you may need to install the `swig` dependency first using Homebrew.

1.  Install `swig`:

    .. code-block:: bash

       brew install swig

2.  Retry the Isek installation:

    .. code-block:: bash

       pip install isek


Installation from Source (for Development)
==========================================

If you wish to install the latest development version directly from the source code, for example, to contribute to the project:

1.  Clone the repository:

    .. code-block:: bash

       git clone <Your-Repository-URL> # e.g., https://github.com/your_org/isek.git
       cd isek

2.  Install in editable mode:

    .. code-block:: bash

       pip install -e .

    The `-e` flag installs the package in "editable" mode, meaning changes you make to the source code will be reflected immediately without needing to reinstall.
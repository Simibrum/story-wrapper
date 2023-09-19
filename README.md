# Story Wrapper

Story Wrapper is a tool for working with longer-form stories. 

It uses spaCy under the hood to parse the text and identify the characters, 
locations and events.

# Story-Wrapper

Your introduction to the project here.

## Table of Contents

- [Project Structure](#project-structure)
- [Setting Up a Local Development Environment](#setting-up-a-local-development-environment)
  - [Creating a Python 3.10 Virtual Environment](#creating-a-python-310-virtual-environment)
  - [Activating the Virtual Environment](#activating-the-virtual-environment)
  - [Installing Dependencies](#installing-dependencies)
- [Running Tests](#running-tests)
  - [Installing pytest](#installing-pytest)
  - [Running Tests with pytest](#running-tests-with-pytest)

## Project Structure

The `story-wrapper` project is structured as a Python package to make it easy to develop and test modules. The directory layout is as follows:

```plaintext
story-wrapper/
├── notebooks/
├── src/
│   └── story_wrapper/
│       └── data_loaders/
│           └── __init__.py
│           └── book.py
│           └── gutenberg.py
│           └── parseRDF.py
│           └── [etc]
│       └── models/
│           └── __init__.py
│           └── story.py
│       └── __init__.py
│       └── config_spacy.py
│       └── utils.py
├── tests/
├── venv/
└── pyproject.toml
```

Each sub-directory in the `story_wrapper` folder should contain an `__init__.py` file to be recognized as a Python package or subpackage.

## Setting Up a Local Development Environment

### Creating a Python 3.10 Virtual Environment

Before you start developing, it's good practice to create a virtual environment. To set up a Python 3.10 virtual environment, run the following command:

```bash
python3.10 -m venv venv
```

### Activating the Virtual Environment

Activate the virtual environment with the appropriate command for your operating system:

- **Unix or macOS**:

  ```bash
  source venv/bin/activate
  ```

- **Windows**:

  ```cmd
  .\venv\Scripts\Activate
  ```

### Installing Dependencies

With the virtual environment activated, navigate to the project's root directory and run:

```bash
pip install -e .
```

This will install the package in "editable" mode, allowing you to make changes to the source code without having to reinstall the package.

## Running Tests

### Installing pytest

To run tests, you'll need to install `pytest` in your virtual environment:

```bash
pip install pytest
```

### Running Tests with pytest

To run your tests, navigate to the project's root directory and execute:

```bash
python -m pytest tests/
```

Using `pytest` as a Python module ensures that the Python environment is consistent with your virtual environment, especially if you have faced import issues.

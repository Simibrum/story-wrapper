# Story Wrapper

Story Wrapper is a tool for working with longer-form stories. 

It uses spaCy under the hood to parse the text and identify the characters, 
locations and events.

## Table of Contents

- [Usage](#usage)
  - [Initializing a Story](#initializing-a-story)
  - [Working with Stories](#working-with-stories)
    - [Accessing Paragraphs](#accessing-paragraphs)
    - [Checking for Paragraphs](#checking-for-paragraphs)
  - [Text Processing and Analysis](#text-processing-and-analysis)
    - [Processing the Story](#processing-the-story)
    - [Unique Entities and Characters](#unique-entities-and-characters)
    - [Counting Characters](#counting-characters)
- [Project Structure](#project-structure)
- [Setting Up a Local Development Environment](#setting-up-a-local-development-environment)
  - [Creating a Python 3.10 Virtual Environment](#creating-a-python-310-virtual-environment)
  - [Activating the Virtual Environment](#activating-the-virtual-environment)
  - [Installing Dependencies](#installing-dependencies)
- [Running Tests](#running-tests)
  - [Installing pytest](#installing-pytest)
  - [Running Tests with pytest](#running-tests-with-pytest)

---

## Usage

### Initializing a Story

The `Story` class can be initialized with a single string or a list of strings. Each string typically represents a paragraph in the story. Optionally, you can specify `process_on_load=True` to automatically process the text using spaCy upon initialization. If not specified, this defaults to `True`.

```python
# Initialize with a single string
story_single = Story("Once upon a time...")
print(len(story_single))  # Output: 1

# Initialize with multiple strings
story_multi = Story(["Once upon a time...", "There was a fox."])
print(len(story_multi))  # Output: 2
```

### Working with Stories

#### Accessing Paragraphs

Individual paragraphs (text blocks) can be accessed using indexing. The class also supports iteration.

```python
# Access a paragraph by index
print(story_multi[0])  # Output: "Once upon a time..."

# Iterate through the paragraphs
for para in story_multi:
    print(para)
```

#### Checking for Paragraphs

You can check if a specific paragraph is present in the story using Python's `in` operator.

```python
# Check if a paragraph exists
if "Once upon a time..." in story_multi:
    print("Found it!")
```

### Text Processing and Analysis

#### Processing the Story

The story text can be processed using spaCy to generate Doc objects, which will allow for more advanced analyses like named entity recognition, part-of-speech tagging, etc. If `process_on_load=True` is not set during initialization, you can manually process the text by calling the `process` method.

```python
docs = story_multi.process()
```

#### Unique Entities and Characters

To get a set of unique entities or characters in the story, you can call the `unique_entities` and `characters` methods, respectively.

```python
unique_entities, entity_spans = story_multi.unique_entities()
print(unique_entities)

characters = story_multi.characters()
print(characters)
```

#### Counting Characters

To get the frequency count of each character in the story, you can use the `count_characters` method, which returns a Counter object.

```python
character_count = story_multi.count_characters()
print(character_count)
```

---

Feel free to adapt this section to fit in your existing README file. It should provide a clear guide to users on how to utilize the `Story` class effectively.

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


### Configuring a Jupyter Notebook Kernel

To use the virtual environment in a Jupyter notebook, you'll need to install the `ipykernel` package:

```bash
pip install ipykernel
```

Then, you can add the virtual environment as a kernel:

```bash
python -m ipykernel install --user --name=story-wrapper
```

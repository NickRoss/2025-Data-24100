# Week #7 Lesson Plan

## Overview

- Wednesday night the next part of the project is due (Part V). You can find the assignment [here](../project_assignments/part_5.md).
- There is a quiz on wednesday.

## Resources

- [MkDocs](https://www.mkdocs.org/) has solid documentation and a good quick start guide.
- [Pytest documentation](https://docs.pytest.org/en/stable/) provides comprehensive information on testing.
- [JSON Schema](https://json-schema.org/) documentation for understanding schema validation.

## Learning Objectives

### Autodocs (MkDocs)

- What is autodocs and why do we use it instead of manual documentation?
- Understand the components of an autodoc system: source code, parser, build system, templates, configuration, and output.
- What are the different autodoc systems (Sphinx, MkDocs, Swagger, Jupyter Book) and when would you use each?
- How to set up MkDocs in a project:
  - Adding dependencies to `pyproject.toml`
  - Creating a new MkDocs project
  - Understanding the file structure (`mkdocs.yml`, `docs/`, `site/`)
- How to configure MkDocs:
  - Understanding the `mkdocs.yml` configuration file
  - Setting up navigation (`nav` section)
  - Configuring themes (material, terminal)
  - Setting up plugins (mkdocstrings)
- How to create and use templates in MkDocs
- Understanding how MkDocs finds files, functions, and modules:
  - The importance of `__init__.py` files
  - How module discovery works
  - Relative vs. absolute imports in the context of autodocs
- How to run and serve autodocs using `make` commands

### Testing Part I

- What is testing and why is it important?
- What are the goals of testing (verify performance, identify defects, validate requirements, ensure components work together)?
- Functional vs. non-functional testing
- How the `assert` function works and when it raises errors
- Types of tests:
  - Unit tests: what they test, pros and cons
  - Integration tests: what they test, how they differ from unit tests
  - End-to-end (E2E) tests: what they test, pros and cons
- What is Test Driven Development (TDD)?
- JSON Schema validation:
  - What is JSON Schema and why use it for validation?
  - Understanding JSON Schema types (string, number, integer, boolean, array, object)
  - Schema properties and constraints (minLength, maxLength, minimum, maximum, required, etc.)
  - How to validate JSON data against a schema using `jsonschema.validate`
- Code coverage: what it is and why it matters

## Lecture notes

[Day 13 (Autodocs)](../class_notes/13_autodocs.md)

[Day 14 (Testing Part I)](../class_notes/14_testing.md)

## Quizzable Concepts

### Autodocs

- What is autodocs and what problem does it solve?
- What are the main components of an autodoc system?
- What is the purpose of the `mkdocs.yml` file?
- How does MkDocs find Python modules and functions? (Why do we need `__init__.py` files?)
- What is the difference between relative and absolute imports in the context of autodocs?
- Be able to read and understand a basic `mkdocs.yml` configuration file
- Understand what the `site/` directory contains and why it shouldn't be in git

### Testing

- What is testing and what are its main goals?
- What is the difference between functional and non-functional testing?
- How does the `assert` function work? What happens when an assertion fails?
- What are unit tests, integration tests, and end-to-end tests? Be able to identify which type a given test is.
- What is Test Driven Development (TDD)?
- What is JSON Schema and why do we use it for validation?
- Be able to read basic JSON Schema definitions for:
  - Simple objects with properties
  - Arrays with typed items
  - Objects with required fields
  - Numbers/strings with constraints (minimum, maximum, minLength, etc.)
- Be able to validate JSON data against a schema using `jsonschema.validate`
- What is code coverage and why is it useful?
- (Review) What are the parts of an HTTP request? Given code for processing and returning a request, be able to describe what the code does.

# Contributing to SwiftAgent

Thank you for your interest in contributing to SwiftAgent! We welcome all kinds of contributions—bug reports, bug fixes, new features, improved documentation, and more.

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Getting Started](#getting-started)  
3. [Development Workflow](#development-workflow)  
   - [Fork & Clone](#fork--clone)  
   - [Setting Up the Environment](#setting-up-the-environment)  
   - [Code Style & Linting](#code-style--linting)  
   - [Testing](#testing)  
   - [Pre-commit Hooks](#pre-commit-hooks)  
4. [Pull Request Guidelines](#pull-request-guidelines)  

---

## Project Overview

SwiftAgent is a Python framework for building scalable, production-ready AI agents, with a web-inspired, decorator-driven architecture. The repository contains:

- Core agent classes and utilities in the `swiftagent/` directory.  
- Example functionalities in the `examples/` directory.  
- Recipes and advanced agent setups in the `cookbook/` directory.  
- Automated tests in the `tests/` directory.  

---

## Getting Started

### 1. Prerequisites

- **Python** 3.10, 3.11 (recommended), 3.12.
- **Git** installed on your machine.

### 2. Installing Dependencies

1. **Clone your fork** of this repository (see [Fork & Clone](#fork--clone) for details).
2. Navigate into the repository directory:

   ```bash
   cd openminder-ai-swiftagent
   ```

3. Install main dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. (Optional) If you plan to run tests or contribute code, also install development dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

5. You can also install the package locally in "editable" mode:

   ```bash
   pip install -e .
   ```

---

## Development Workflow

### Fork & Clone

1. **Fork** the repository on GitHub by clicking the "Fork" button at the top right of the repository page.  
2. **Clone** your fork locally:
   
   ```bash
   git clone https://github.com/<your-username>/swiftagent.git
   ```

3. **Configure upstream remote** (so you can pull updates from the main repository):

   ```bash
   cd swiftagent
   git remote add upstream https://github.com/openminder-ai/SwiftAgent.git
   ```

> **Tip:** Keep your `main` branch synced with the upstream repository’s `main` by regularly pulling in changes.  

### Setting Up the Environment

- It is recommended to work within a virtual environment to isolate dependencies:
  
  ```bash
  python -m venv venv
  source venv/bin/activate      # Mac/Linux
  # or
  venv\Scripts\activate.bat     # Windows
  ```

- Once activated, install the dependencies as described above.

### Code Style & Linting

We use **Black** for code formatting:

- A Black configuration is provided via [`.pre-commit-config.yaml`](./.pre-commit-config.yaml).  
- Black defaults to an 80-character line length in this repository.  

Additionally, we encourage consistent naming, docstrings, and Pythonic code.  

### Testing

1. **Unit Tests:** All tests are located in the [`tests/`](./tests/) directory.  
2. **Running tests locally:**

   ```bash
   pytest --cov=swiftagent --cov-report=term-missing
   ```

   This command runs the tests and displays a coverage report.

3. **Coverage:** We aim to keep coverage high. If you add functionality, please also add tests for it.

### Pre-commit Hooks

This project uses **pre-commit** to run linting and formatting checks automatically before any commit.

1. **Install pre-commit** hooks locally once:

   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Run hooks on-demand** (optional) to check all files:

   ```bash
   pre-commit run --all-files
   ```

If any checks fail, fix the issues (e.g., let Black reformat your files) and re-commit.

---

## Pull Request Guidelines

1. **Create a Branch**  
   For any new feature or fix, create a separate branch in your fork:

   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Implement & Test**  
   - Add or modify code in the `swiftagent/`, `examples/`, or `cookbook/` directories as needed.  
   - Keep the code style consistent.  
   - Add or update tests under `tests/` to cover your changes.

3. **Commit**  
   - Make atomic commits with clear, descriptive messages.  
   - Ensure you run the pre-commit checks:

     ```bash
     pre-commit run --all-files
     ```

   - Resolve any lint, formatting, or testing issues.

4. **Push & Open a Pull Request**  
   - Push your branch to your fork:

     ```bash
     git push origin feature/my-new-feature
     ```

   - Go to your fork on GitHub, and click "Compare & pull request" to open a PR into the `main` branch of the official `openminder-ai/SwiftAgent` repository.  
   - In the Pull Request description:
     - Explain the rationale for your changes.
     - Reference any issues if relevant (`Closes #IssueNumber`).
     - Provide screenshots or logs if it’s UI- or output-related.

5. **Address Feedback**  
   - The maintainers may comment on your PR with questions or suggestions.  
   - Keep an eye on your PR notifications and push new commits to address feedback.  
   - Once all checks pass and reviews are approved, a maintainer will merge your changes.

---

That’s it! Your contribution is now part of SwiftAgent. Thank you again for your support and involvement.

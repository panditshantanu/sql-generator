# Contributing to SQL Generator

We welcome contributions to the SQL Generator project! This guide will help you get started.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)
- [Issue Guidelines](#issue-guidelines)

## 🤝 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/). By participating, you agree to uphold this code.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of semantic search and vector databases

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/shantanupandit/sql-generator.git
cd sql-generator
```

3. Add the upstream repository:

```bash
git remote add upstream https://github.com/shantanupandit/sql-generator.git
```

## 🛠️ Development Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install in development mode with all extras
pip install -e ".[dev,all]"

# Or install from requirements
pip install -r requirements.txt
```

### 3. Setup Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Test pre-commit (optional)
pre-commit run --all-files
```

### 4. Initialize Test Environment

```bash
# Setup test embeddings
python -m sql_generator.cli --setup

# Run tests to verify setup
pytest
```

## 🔄 Making Changes

### 1. Create a Branch

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### 2. Development Workflow

1. **Write tests first** (TDD approach recommended)
2. **Implement your changes**
3. **Run tests** to ensure everything works
4. **Update documentation** if needed
5. **Commit your changes** with clear messages

### 3. Commit Messages

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `perf`: Performance improvements

**Examples:**
```bash
git commit -m "feat(search): add confidence threshold filtering"
git commit -m "fix(embeddings): resolve ChromaDB collection initialization"
git commit -m "docs(api): update SQLGenerator class documentation"
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sql_generator --cov-report=html

# Run specific test file
pytest tests/unit/test_schema_searcher.py

# Run tests with verbose output
pytest -v

# Run tests matching a pattern
pytest -k "test_search"
```

### Writing Tests

1. **Place tests in the `tests/` directory**
2. **Use descriptive test names**
3. **Follow the AAA pattern** (Arrange, Act, Assert)
4. **Mock external dependencies**

**Example test:**

```python
import pytest
from sql_generator.schema import SchemaSearcher

class TestSchemaSearcher:
    def test_search_returns_results(self):
        # Arrange
        searcher = SchemaSearcher()
        query = "customer information"
        
        # Act
        results = searcher.search(query, n_results=5)
        
        # Assert
        assert isinstance(results, list)
        assert len(results) <= 5
        for result in results:
            assert 'score' in result
            assert 'content' in result

    def test_search_filters_by_confidence(self):
        # Arrange
        searcher = SchemaSearcher()
        
        # Act
        results = searcher.search(
            "test query", 
            n_results=10,
            score_threshold=0.3
        )
        
        # Assert
        for result in results:
            assert result['score'] >= 0.3
```

### Test Categories

1. **Unit Tests** (`tests/unit/`) - Test individual components
2. **Integration Tests** (`tests/integration/`) - Test component interactions
3. **End-to-End Tests** (`tests/e2e/`) - Test complete workflows

## 📝 Style Guidelines

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking
- **isort** for import sorting

### Running Style Checks

```bash
# Format code with Black
black sql_generator/

# Check with Flake8
flake8 sql_generator/

# Type checking with MyPy
mypy sql_generator/

# Sort imports
isort sql_generator/

# Run all checks
pre-commit run --all-files
```

### Python Style Guidelines

1. **Follow PEP 8**
2. **Use type hints** for all functions
3. **Write descriptive docstrings**
4. **Keep functions small and focused**
5. **Use meaningful variable names**

**Example:**

```python
from typing import List, Dict, Optional

def search_schema(
    query: str, 
    n_results: int = 10,
    confidence_threshold: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Search for relevant schema elements using semantic similarity.
    
    Args:
        query: Natural language search query
        n_results: Maximum number of results to return
        confidence_threshold: Minimum confidence score for filtering
        
    Returns:
        List of search results with scores and metadata
        
    Raises:
        SearchError: If search operation fails
    """
    # Implementation here
    pass
```

### Documentation Style

1. **Use clear, concise language**
2. **Include code examples**
3. **Document all public APIs**
4. **Keep README up to date**

## 🚀 Submitting Changes

### 1. Ensure Quality

Before submitting, make sure:

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)
- [ ] Commit messages are clear

### 2. Push Changes

```bash
# Push your branch
git push origin feature/your-feature-name
```

### 3. Create Pull Request

1. **Go to GitHub** and create a pull request
2. **Use the PR template** (if available)
3. **Write a clear description** of your changes
4. **Link related issues**

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes

## Related Issues
Fixes #(issue number)
```

### 4. Address Review Comments

- **Respond promptly** to review feedback
- **Make requested changes** in new commits
- **Ask questions** if feedback is unclear
- **Test changes** after modifications

## 📋 Issue Guidelines

### Reporting Bugs

Use the bug report template:

```markdown
**Bug Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. See error

**Expected Behavior**
What you expected to happen

**Environment**
- OS: [e.g. Windows 10]
- Python Version: [e.g. 3.9]
- SQL Generator Version: [e.g. 1.0.0]

**Additional Context**
Any other context about the problem
```

### Feature Requests

Use the feature request template:

```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other solutions you've considered

**Additional Context**
Any other context or screenshots
```

## 🏗️ Architecture Guidelines

### Adding New Components

1. **Follow existing patterns**
2. **Keep components focused** on single responsibility
3. **Use dependency injection** where appropriate
4. **Add proper error handling**
5. **Include comprehensive tests**

### Directory Structure

```
sql_generator/
├── core/           # Core business logic
├── schema/         # Schema processing
├── llm/           # LLM integration  
├── utils/         # Utility functions
└── cli.py         # Command-line interface
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `SchemaSearcher`)
- **Functions/Methods**: snake_case (e.g., `search_schema`)
- **Variables**: snake_case (e.g., `confidence_score`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_THRESHOLD`)

## 🐛 Debugging Guidelines

### Common Issues

1. **Collection Not Found**
   - Run `python -m sql_generator.cli --setup`
   - Check ChromaDB initialization

2. **Import Errors**
   - Verify installation: `pip install -e .`
   - Check Python path configuration

3. **Low Test Coverage**
   - Add tests for new functions
   - Test edge cases and error conditions

### Debugging Tools

```bash
# Run with verbose logging
python -m sql_generator.cli --verbose --query "test"

# Debug specific component
python -c "
from sql_generator.schema import SchemaSearcher
searcher = SchemaSearcher(verbose=True)
results = searcher.search('test')
print(results)
"

# Profile performance
python -m cProfile -o profile.stats your_script.py
```

## 📚 Resources

### Learning Resources

- [Semantic Search Fundamentals](https://www.sbert.net/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Testing with Pytest](https://docs.pytest.org/)

### Project Resources

- [GitHub Repository](https://github.com/shantanupandit/sql-generator)
- [Issue Tracker](https://github.com/shantanupandit/sql-generator/issues)
- [Discussions](https://github.com/shantanupandit/sql-generator/discussions)

## 🙏 Recognition

Contributors will be recognized in:

- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **GitHub contributors** page

## 📞 Getting Help

- **GitHub Discussions** for questions
- **GitHub Issues** for bugs and features
- **Email** mishantanupandit@gmail.com for sensitive issues

Thank you for contributing to SQL Generator! 🚀

# Contributing to IndiVillage Voice Agent System

Thank you for your interest in contributing to the IndiVillage Voice Agent System! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

1. **Check existing issues** first to avoid duplicates
2. **Use the issue template** when creating new issues
3. **Provide detailed information** including:
   - Steps to reproduce the problem
   - Expected vs actual behavior
   - Environment details (OS, Python version, browser)
   - Error messages and logs

### Submitting Changes

1. **Fork the repository**
2. **Create a feature branch** from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following our coding standards
4. **Test thoroughly** including edge cases
5. **Commit with clear messages** following our commit conventions
6. **Push to your fork** and create a pull request

## 📋 Development Setup

### Prerequisites
- Python 3.12+
- Node.js 16+ (for frontend dependencies)
- Git
- Modern web browser

### Local Development
```bash
# Clone your fork
git clone https://github.com/your-username/voice-agent-system.git
cd voice-agent-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run tests
python -m pytest

# Start development server
python client.py
```

## 🎯 Coding Standards

### Python Code Style
- Follow **PEP 8** guidelines
- Use **Black** for code formatting
- Use **isort** for import sorting
- Maximum line length: **88 characters**
- Use **type hints** where appropriate

### JavaScript/HTML/CSS
- Use **Prettier** for formatting
- Follow **ES6+** standards
- Use **semantic HTML**
- Follow **BEM methodology** for CSS classes

### Documentation
- Use **Google-style docstrings** for Python functions
- Include **type annotations**
- Update **README.md** for significant changes
- Add **inline comments** for complex logic

## 🧪 Testing Guidelines

### Test Structure
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── fixtures/       # Test data and fixtures
└── conftest.py     # Pytest configuration
```

### Writing Tests
- **Test file naming**: `test_*.py`
- **Test function naming**: `test_function_name_scenario`
- **Use fixtures** for common test data
- **Mock external dependencies** (APIs, databases)
- **Aim for 80%+ code coverage**

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.

# Run specific test file
python -m pytest tests/unit/test_business_logic.py

# Run tests matching pattern
python -m pytest -k "test_customer"
```

## 🏗️ Architecture Guidelines

### Code Organization
- **Separation of concerns**: Keep business logic separate from presentation
- **Single responsibility**: Each function/class should have one purpose
- **DRY principle**: Don't repeat yourself
- **SOLID principles**: Follow object-oriented design principles

### Adding New Features

#### Voice Agent Functions
1. Add function definition to `common/agent_functions.py`
2. Add function mapping to `FUNCTION_MAP`
3. Update `FUNCTION_DEFINITIONS` for the AI agent
4. Add corresponding business logic to `common/business_logic.py`
5. Write comprehensive tests

#### Knowledge Base Entries
1. Create MDX file in `knowledgebase/mdx/`
2. Follow existing frontmatter structure
3. Use consistent tagging and categorization
4. Test search functionality

#### Web Interface Changes
1. Update HTML templates in `templates/`
2. Add CSS styles to `static/style.css`
3. Update JavaScript in template files
4. Test across different browsers

## 🔄 Git Workflow

### Branch Naming
- **Feature branches**: `feature/description-of-feature`
- **Bug fixes**: `fix/description-of-bug`
- **Documentation**: `docs/description-of-change`
- **Refactoring**: `refactor/description-of-change`

### Commit Messages
Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

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
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(voice): add support for multiple languages
fix(appointments): resolve timezone handling bug
docs(readme): update installation instructions
test(business): add tests for customer creation
```

### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** if applicable
5. **Request review** from maintainers
6. **Address feedback** promptly
7. **Squash commits** if requested

## 🐛 Debugging Guidelines

### Common Issues
- **Audio not working**: Check browser permissions and device selection
- **API errors**: Verify Deepgram API key configuration
- **Database issues**: Check mock data file permissions
- **WebSocket errors**: Ensure proper connection handling

### Debugging Tools
- **Browser DevTools**: For frontend debugging
- **Python debugger**: Use `pdb` or IDE debuggers
- **Logging**: Use the custom log formatter for structured logging
- **Network tab**: Monitor WebSocket and HTTP requests

## 📚 Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SocketIO Documentation](https://python-socketio.readthedocs.io/)
- [Deepgram API Docs](https://developers.deepgram.com/)
- [MDX Documentation](https://mdxjs.com/)

### Tools
- [Black Code Formatter](https://black.readthedocs.io/)
- [isort Import Sorter](https://pycqa.github.io/isort/)
- [Pytest Testing Framework](https://docs.pytest.org/)
- [Pre-commit Hooks](https://pre-commit.com/)

## 🏷️ Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested
- `wontfix`: This will not be worked on

## 📞 Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For questions and general discussion
- **Code Review**: Request reviews from maintainers
- **Documentation**: Check existing docs first

## 🎉 Recognition

Contributors will be recognized in:
- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **GitHub contributors** section

Thank you for contributing to IndiVillage Voice Agent System! 🚀
# Contributing

First of all, thank you for your interest in contributing to ChatIQ! When contributing to this project, please first discuss the change you wish to make via issue before making a change.

Please note that this project has a [code of conduct](https://github.com/yujiosaka/ChatIQ/blob/main/.github/CODE_OF_CONDUCT.md). Please follow it in all your interactions with this project.

## Contributing Process

1. Make sure to set up your local environment according to the instructions in README.md. 

2. Follow Python's PEP 8 style guide. Additionally, we use [Black](https://github.com/psf/black) for code formatting, [isort](https://pycqa.github.io/isort/) for import sorting, and [flake8](https://flake8.pycqa.org/en/latest/) for code linting. Ensure your code complies with all these tools. They are set up to run automatically on commit via pre-commit hooks.

3. Type annotations should be added wherever possible. We use Python's built-in `typing` module for this purpose.

4. Make sure all tests pass by running `pytest` from the command line. Modify existing tests if necessary and add new ones when introducing new features or fixing bugs. Test coverage is important to us.

5. Update the [README.md](https://github.com/yujiosaka/ChatIQ/blob/main/README.md) if you have made changes to the interface or added significant new features.

6. Make your commit message following [Conventional Commits](https://conventionalcommits.org/). The versioning scheme we use is [Semantic Versioning](http://semver.org/spec/v2.0.0.html) which is automated by [semantic-release](https://github.com/semantic-release/semantic-release).

7. Make a Pull Request against the `main` branch. You may request a reviewer to merge your commit.

Thank you again for taking the time to contribute!

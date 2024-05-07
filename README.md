# Jac-Analyzer

[![Language Server Tests](https://github.com/Jaseci-Labs/jac-analyzer/actions/workflows/ls_tests.yml/badge.svg?branch=main)](https://github.com/Jaseci-Labs/jac-analyzer/actions/workflows/ls_tests.yml)

The Jac-Analyzer is a Visual Studio Code extension that provides Language Server Protocol (LSP) functionalities for the Jaclang programming language. Jaclang is a versatile and powerful language developed by Jaseci-Labs for building complex systems.

## Features

- Syntax Highlighting
- Semantic Syntax Highlighting
- Error Diagnostics
- Go-to Definition
- Go-to Implementation
- Hover Information

## Commands

| Command                | Description                         |
| ---------------------- | ----------------------------------- |
| jaclang: Restart Server | Force restart the language server. |
| jaclang: Run Tests      | Run tests in the workspace. | 
| jaclang: Run File       | Run the file in the workspace. |
| jaclang: Clear Cache    | Clear the cache. |

## Settings

| Settings | Default | Description |
| -------- | ------- | ----------- |
| jaclang.severity | `{ "error": "Error", "note": "Information" }` | Controls mapping of severity from `jaclang` to VS Code severity when displaying in the problems window. You can override specific `jac` error codes `{ "error": "Error", "note": "Information", "name-defined": "Warning" }` |
| jaclang.interpreter | `[]` | Path to a Python interpreter to use to run the jaclang language server. When set to `[]`, the interpreter for the workspace is obtained from the `ms-python.python` extension. If set to a specific path, that path takes precedence and the Python extension is not queried for the interpreter. |
| jaclang.importStrategy | `useBundled` | Setting to choose where to load `jaclang` from. `useBundled` picks the bundled `jaclang` with the extension. `fromEnvironment` uses the `jaclang` available in the environment. |
| jaclang.showNotifications | `off` | Setting to control when a notification is shown. |
| jaclang.reportingScope | `file` | (experimental) Setting to control if problems are reported for files open in the editor (`file`) or for the entire workspace (`workspace`). |
| jaclang.showWarnings | `false` | Setting to control if warnings are shown in the file/workspace |

## Contributing

### Prerequisites

- [Node.js](https://nodejs.org/en/)
- [VS Code](https://code.visualstudio.com/)
- [Python](https://www.python.org/) (3.12)
  - [Conda](https://docs.conda.io/en/latest/) (optional) `conda create -n jac-analyzer python=3.13 -y`

### Setup

Install Nox
```bash
pip install nox
```
Install Dependencies
```bash
nox --session setup
```
You are now ready to run the extension in a development environment. Follow Debugging instructions below.

### Build
To build the `.vsix` and Then you can install the extension on your VSCode using this <https://code.visualstudio.com/docs/editor/extension-marketplace>

```bash
npm run vsce-package
```

### Running Tests

To run language server tests

```bash
pytest
```

### Debugging
Go to the debug view in VSCode and select `Debug Extension and Python` from the dropdown. Then press the play button to start the extension in debug mode with debugpy attached.
Select the `Debug Extension Only` option to start the extension without attaching to the language server.

### Using Local Jaclang
If you want to use a local version of Jaclang, you can set the `jaclang.importStrategy` setting to `fromEnvironment` and set the '`jaclang.interpreter` setting to the path of the Python interpreter that has Jaclang installed (use `which python` to find the path).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
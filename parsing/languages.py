"""Language detection and tree-sitter grammar loading."""

import os
from tree_sitter import Language, Parser
from core.constants import LANGUAGE_EXTENSIONS


# Grammar modules per language
_GRAMMAR_MODULES = {
    "python": "tree_sitter_python",
    "javascript": "tree_sitter_javascript",
    "typescript": "tree_sitter_typescript",
}


def detect_language(file_path: str) -> str:
    """Detect programming language from file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    for language, extensions in LANGUAGE_EXTENSIONS.items():
        if ext in extensions:
            return language
    return "unknown"


def get_parser(language: str) -> Parser:
    """Load tree-sitter parser for the given language."""
    import importlib

    module_name = _GRAMMAR_MODULES.get(language)
    if not module_name:
        raise ValueError(f"No tree-sitter grammar for language: {language}")

    mod = importlib.import_module(module_name)

    # tree-sitter-typescript exposes .language_typescript() and .language_tsx()
    if language == "typescript" and hasattr(mod, "language_typescript"):
        lang = Language(mod.language_typescript())
    else:
        lang = Language(mod.language())

    return Parser(lang)

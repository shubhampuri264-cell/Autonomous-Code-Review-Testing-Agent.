"""Core AST analysis using tree-sitter."""

import os
from typing import Tuple

from parsing.languages import get_parser, detect_language


async def analyze_codebase(
    local_path: str,
    file_list: list[str],
    languages: list[str],
) -> Tuple[dict, dict]:
    """Parse all source files and return AST map + file summaries.

    Returns:
        ast_map: {file_path: {functions, classes, imports, node_count, language}}
        file_summaries: {file_path: human-readable summary string}
    """
    ast_map = {}
    file_summaries = {}

    for file_path in file_list:
        full_path = os.path.join(local_path, file_path)
        language = detect_language(file_path)

        if language not in languages:
            continue

        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()

        parser = get_parser(language)
        tree = parser.parse(bytes(source, "utf-8"))
        root = tree.root_node

        # Extract functions, classes, imports
        functions = _extract_functions(root, language)
        classes = _extract_classes(root, language)
        imports = _extract_imports(root, language)
        node_count = _count_nodes(root)

        ast_map[file_path] = {
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "node_count": node_count,
            "language": language,
        }

        file_summaries[file_path] = (
            f"{len(functions)} functions, {len(classes)} classes, "
            f"{node_count} AST nodes"
        )

    return ast_map, file_summaries


def _extract_functions(node, language: str) -> list[dict]:
    """Extract function definitions from AST."""
    functions = []
    target_type = "function_definition" if language == "python" else "function_declaration"

    for child in _walk(node):
        if child.type == target_type:
            name_node = child.child_by_field_name("name")
            if name_node:
                functions.append({
                    "name": name_node.text.decode("utf-8"),
                    "start_line": child.start_point[0],
                    "end_line": child.end_point[0],
                })
    return functions


def _extract_classes(node, language: str) -> list[dict]:
    """Extract class definitions from AST."""
    classes = []
    for child in _walk(node):
        if child.type == "class_definition" or child.type == "class_declaration":
            name_node = child.child_by_field_name("name")
            if name_node:
                classes.append({
                    "name": name_node.text.decode("utf-8"),
                    "start_line": child.start_point[0],
                    "end_line": child.end_point[0],
                })
    return classes


def _extract_imports(node, language: str) -> list[str]:
    """Extract import statements from AST."""
    imports = []
    for child in _walk(node):
        if child.type in ("import_statement", "import_from_statement", "import_declaration"):
            imports.append(child.text.decode("utf-8"))
    return imports


def _count_nodes(node) -> int:
    """Count total AST nodes (proxy for complexity)."""
    count = 1
    for child in node.children:
        count += _count_nodes(child)
    return count


def _walk(node):
    """Recursively walk all AST nodes."""
    yield node
    for child in node.children:
        yield from _walk(child)

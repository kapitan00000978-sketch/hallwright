"""Hallwright Enterprise Copywriting Library: AST Documentation Generator.

Parses Python source code and generates publication-grade GitHub Flavored Markdown
reference documentation including signatures, types, docstrings, and usage tables.
"""

import ast
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class DocFunction:
    """Documented function or method."""
    name: str
    signature: str
    docstring: str
    is_async: bool = False
    args: List[str] = field(default_factory=list)
    return_type: Optional[str] = None


@dataclass
class DocClass:
    """Documented class representation."""
    name: str
    docstring: str
    methods: List[DocFunction] = field(default_factory=list)


@dataclass
class DocModule:
    """Documented module containing classes and standalone functions."""
    name: str
    docstring: str
    classes: List[DocClass] = field(default_factory=list)
    functions: List[DocFunction] = field(default_factory=list)


class MarkdownDocGenerator:
    """Generates markdown API documentation from Python ASTs."""

    @classmethod
    def parse_source(cls, source_code: str, module_name: str = "module") -> DocModule:
        """Parse source code into structured documentation models."""
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return DocModule(name=module_name, docstring="Syntax error in source code.")

        mod_doc = ast.get_docstring(tree) or ""
        doc_mod = DocModule(name=module_name, docstring=mod_doc)

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                cls_doc = ast.get_docstring(node) or ""
                doc_cls = DocClass(name=node.name, docstring=cls_doc)

                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        doc_cls.methods.append(cls._parse_function(item))

                doc_mod.classes.append(doc_cls)

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc_mod.functions.append(cls._parse_function(node))

        return doc_mod

    @classmethod
    def _parse_function(cls, node: Any) -> DocFunction:
        """Extract signature and metadata from function AST node."""
        doc = ast.get_docstring(node) or ""
        is_async = isinstance(node, ast.AsyncFunctionDef)
        args_list = []

        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                try:
                    arg_str += f": {ast.unparse(arg.annotation)}"
                except Exception as ann_err:
                    arg_str += ": Any"
            args_list.append(arg_str)

        ret_type = None
        if node.returns:
            try:
                ret_type = ast.unparse(node.returns)
            except Exception as ret_err:
                ret_type = "Any"

        sig = f"{'async ' if is_async else ''}def {node.name}({', '.join(args_list)})"
        if ret_type:
            sig += f" -> {ret_type}"

        return DocFunction(
            name=node.name,
            signature=sig,
            docstring=doc,
            is_async=is_async,
            args=args_list,
            return_type=ret_type,
        )

    @classmethod
    def to_markdown(cls, doc_mod: DocModule) -> str:
        """Render DocModule into clean GitHub Flavored Markdown."""
        lines = [
            f"# API Reference: `{doc_mod.name}`",
            "",
            doc_mod.docstring if doc_mod.docstring else "No module description provided.",
            "",
        ]

        if doc_mod.classes:
            lines.append("## Classes")
            lines.append("")
            for cl in doc_mod.classes:
                lines.append(f"### `class {cl.name}`")
                lines.append("")
                if cl.docstring:
                    lines.append(f"> {cl.docstring.strip()}")
                    lines.append("")

                if cl.methods:
                    lines.append("#### Methods")
                    lines.append("")
                    for m in cl.methods:
                        lines.append(f"```python\n{m.signature}\n```")
                        if m.docstring:
                            lines.append(m.docstring.strip())
                        lines.append("")

        if doc_mod.functions:
            lines.append("## Functions")
            lines.append("")
            for f in doc_mod.functions:
                lines.append(f"### `{f.name}()`")
                lines.append("")
                lines.append(f"```python\n{f.signature}\n```")
                if f.docstring:
                    lines.append(f.docstring.strip())
                lines.append("")

        return "\n".join(lines)

import os
from typing import List

from pygls.server import LanguageServer
from lsprotocol.types import (
    TextDocumentItem,
    SymbolInformation,
    SymbolKind,
    Location,
    Range,
    Position,
)

from jaclang.jac.passes import Pass
from jaclang.jac.passes.blue.ast_build_pass import AstBuildPass
import jaclang.jac.absyntree as ast
from jaclang.jac.transpiler import jac_file_to_pass


def fill_workspace(ls: LanguageServer):
    """
    Fill the workspace with all the JAC files
    """
    jac_files = [
        os.path.join(root, name)
        for root, _, files in os.walk(ls.workspace.root_path)
        for name in files
        if name.endswith(".jac")
    ]
    for file_ in jac_files:
        text = open(file_, "r").read()
        doc = TextDocumentItem(
            uri=f"file://{file_}", language_id="jac", version=0, text=text
        )
        ls.workspace.put_document(doc)
        doc = ls.workspace.get_document(doc.uri)
        update_doc_tree(ls, doc.uri)
    for doc in ls.workspace.documents.values():
        update_doc_deps(ls, doc.uri)
    ls.workspace_filled = True


def update_doc_tree(ls: LanguageServer, doc_uri: str):
    """
    Update the tree of a document and its symbols
    """
    doc = ls.workspace.get_document(doc_uri)
    doc.symbols = [s for s in get_doc_symbols(ls, doc.uri) if s.location.uri == doc.uri]
    update_doc_deps(ls, doc.uri)


def update_doc_deps(ls: LanguageServer, doc_uri: str):
    """
    Update the dependencies of a document
    """
    doc = ls.workspace.get_document(doc_uri)
    doc.dependencies = {}
    import_prse = jac_file_to_pass(
        file_path=doc.path, target=ImportPass, schedule=[AstBuildPass, ImportPass]
    )
    ls.dep_table[doc.path] = [s for s in import_prse.output if s["is_jac_import"]]
    for dep in import_prse.output:
        if dep["is_jac_import"]:
            architypes = _get_architypes_from_jac_file(
                os.path.join(os.path.dirname(doc.path), dep["path"])
            )
            new_symbols = get_doc_symbols(
                ls,
                f"file://{os.path.join(os.path.dirname(doc.path), dep['path'], '.jac')}",
                architypes=architypes,
            )
            dependencies = {
                dep["path"]: {"architypes": architypes, "symbols": new_symbols}
            }
            doc.dependencies.update(dependencies)


def get_symbol_data(ls: LanguageServer, uri: str, name: str, architype: str):
    """
    Return the data of a symbol
    """
    doc = ls.workspace.get_document(uri)
    if not hasattr(doc, "symbols"):
        doc.symbols = get_doc_symbols(ls, doc.uri)

    symbols_pool = doc.symbols
    # TODO: Extend the symbols pool to include symbols from dependencies

    for symbol in symbols_pool:
        if symbol.name == name and symbol.kind == _get_symbol_kind(architype):
            return symbol
    else:
        return None


def get_doc_symbols(
    ls: LanguageServer,
    doc_uri: str,
    architypes: dict[str, list] = None,
    shift_lines: int = 0,
) -> List[SymbolInformation]:
    """
    Return a list of symbols in the document
    """
    if architypes is None:
        architypes = _get_architypes(ls, doc_uri)

    symbols: List[SymbolInformation] = []

    for architype in architypes.keys():
        for element in architypes[architype]:
            symbols.append(
                SymbolInformation(
                    name=element["name"],
                    kind=_get_symbol_kind(architype),
                    location=Location(
                        uri=doc_uri,
                        range=Range(
                            start=Position(
                                line=(element["line"] - 1) + shift_lines,
                                character=element["col"],
                            ),
                            end=Position(
                                line=element["block_end"]["line"] + shift_lines,
                                character=0,
                            ),
                        ),
                    ),
                )
            )
            for var in element["vars"]:
                symbols.append(
                    SymbolInformation(
                        name=var["name"],
                        kind=_get_symbol_kind(var["type"]),
                        location=Location(
                            uri=doc_uri,
                            range=Range(
                                start=Position(
                                    line=var["line"] - 1 + shift_lines,
                                    character=var["col"],
                                ),
                                end=Position(
                                    line=var["line"] + shift_lines,
                                    character=var["col"] + len(var["name"]),
                                ),
                            ),
                        ),
                        container_name=element["name"],
                    )
                )
    return symbols


def _get_architypes(ls: LanguageServer, doc_uri: str) -> dict[str, list]:
    """
    Return a dictionary of architypes in the document including their elements
    """
    doc = ls.workspace.get_document(doc_uri)
    architype_prse = jac_file_to_pass(
        file_path=doc.path, target=ArchitypePass, schedule=[AstBuildPass, ArchitypePass]
    )
    doc.architypes = architype_prse.output
    return doc.architypes if doc.architypes else {}


def _get_architypes_from_jac_file(file_path: str) -> dict[str, list]:
    """
    Return a dictionary of architypes in the document including their elements
    """
    architype_prse = jac_file_to_pass(
        file_path=file_path,
        target=ArchitypePass,
        schedule=[AstBuildPass, ArchitypePass],
    )
    return architype_prse.output


def _get_symbol_kind(architype: str) -> SymbolKind:
    """
    Return the symbol kind of an architype
    """
    if architype == "walker":
        return SymbolKind.Class
    elif architype == "node":
        return SymbolKind.Class
    elif architype == "edge":
        return SymbolKind.Interface
    elif architype == "graph":
        return SymbolKind.Namespace
    elif architype == "ability":
        return SymbolKind.Method
    elif architype == "object":
        return SymbolKind.Object
    else:
        return SymbolKind.Variable


class ArchitypePass(Pass):
    """
    A pass that extracts architypes from a JAC file
    """

    output = {"walker": [], "node": [], "edge": [], "graph": [], "object": []}
    output_key_map = {
        "KW_NODE": "node",
        "KW_WALKER": "walker",
        "KW_EDGE": "edge",
        "KW_GRAPH": "graph",
        "KW_OBJECT": "object",
    }

    def extract_vars(self, nodes: List[ast.AstNode]):
        vars = []
        for node in nodes:
            if isinstance(node, ast.Ability):
                try:
                    vars.append(
                        {
                            "type": "ability",
                            "name": node.name_ref.value,
                            "line": node.line,
                            "col": node.name_ref.col_start,
                        }
                    )
                except Exception as e:
                    print(node.to_dict(), e)
            elif isinstance(node, ast.ArchHas):
                for var in node.vars.kid:
                    vars.append(
                        {
                            "type": "has_var",
                            "name": var.name.value,
                            "line": var.line,
                            "col": var.name.col_start,
                        }
                    )
        return vars

    def enter_architype(self, node: ast.Architype):
        architype = {}
        architype["name"] = node.name.value
        architype["line"] = node.name.line
        architype["col"] = node.name.col_start

        architype["vars"] = self.extract_vars(node.body.kid)
        architype["block_end"] = {"line": 0, "col": 0}  # TODO: fix this
        architype["block_start"] = {"line": 0, "col": 0}  # TODO: fix this

        self.output[self.output_key_map[node.arch_type.name]].append(architype)


class ImportPass(Pass):
    """
    A pass that extracts imports from a JAC file
    """

    output = []

    def enter_import(self, node: ast.Import):
        self.output.append(
            {
                "is_jac_import": node.lang.value == "jac",
                "path": node.path.path_str,
                "line": node.line,
            }
        )


class ReferencePass(Pass):
    """
    A pass that extracts references from a JAC file
    """

    output = []

    def enter_node(self, node: ast.AstNode):
        pass

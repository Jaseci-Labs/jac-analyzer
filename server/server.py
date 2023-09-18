import re
from typing import Optional

from .utils.validation import _validate
from .utils.completion import _get_completion_items
from .utils.utils import update_doc_tree, get_doc_symbols, fill_workspace

from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DEFINITION,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_CLOSE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_SAVE,
    TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    TEXT_DOCUMENT_DOCUMENT_SYMBOL,
    WORKSPACE_SYMBOL,
)
from lsprotocol.types import (
    CompletionList,
    CompletionParams,
    DefinitionParams,
    DocumentSymbolParams,
    WorkspaceSymbolParams,
    DidChangeTextDocumentParams,
    DidCloseTextDocumentParams,
    DidOpenTextDocumentParams,
    DidSaveTextDocumentParams,
    SemanticTokens,
    SemanticTokensLegend,
    SemanticTokensParams,
)
from pygls.server import LanguageServer


class JaclangLanguageServer(LanguageServer):
    CONFIGURATION_SECTION = "jaseci"

    def __init__(self, *args):
        super().__init__(*args)
        self.workspace_filled = False
        self.dep_table = {}


jaclang_server = JaclangLanguageServer("pygls-jaclang", "v0.0.1-alpha")


@jaclang_server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls, params: DidChangeTextDocumentParams):
    """Stuff to happen on text document did change"""
    update_doc_tree(ls, params.text_document.uri)
    _validate(ls, params)


@jaclang_server.feature(TEXT_DOCUMENT_DID_SAVE)
def did_save(ls, params: DidSaveTextDocumentParams):
    """Stuff to happen on text document did save"""
    update_doc_tree(ls, params.text_document.uri)
    _validate(ls, params)


@jaclang_server.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(server: JaclangLanguageServer, params: DidCloseTextDocumentParams):
    """Stuff to happen on text document did close"""
    server.show_message("Text Document Did Close")


@jaclang_server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls, params: DidOpenTextDocumentParams):
    """Stuff to happen on text document did open"""
    if not ls.workspace_filled:
        fill_workspace(ls)
    _validate(ls, params)


@jaclang_server.feature(TEXT_DOCUMENT_COMPLETION)
def completions(params: Optional[CompletionParams] = None) -> CompletionList:
    """Returns completion items."""
    completion_items = _get_completion_items(jaclang_server, params)
    return CompletionList(is_incomplete=False, items=completion_items)


@jaclang_server.feature(WORKSPACE_SYMBOL)
def workspace_symbol(ls: JaclangLanguageServer, params: WorkspaceSymbolParams):
    """Workspace symbols."""
    symbols = []
    for doc in ls.workspace.documents.values():
        if hasattr(doc, "symbols"):
            symbols.extend(doc.symbols)
        else:
            doc.symbols = get_doc_symbols(ls, doc.uri)
            symbols.extend(doc.symbols)
    return symbols


@jaclang_server.feature(TEXT_DOCUMENT_DOCUMENT_SYMBOL)
def document_symbol(ls: JaclangLanguageServer, params: DocumentSymbolParams):
    """Document symbols."""
    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)
    if not hasattr(doc, "symbols"):
        update_doc_tree(ls, doc.uri)
        doc_symbols = get_doc_symbols(ls, doc.uri)
        return [s for s in doc_symbols if s.location.uri == doc.uri]
    else:
        return [s for s in doc.symbols if s.location.uri == doc.uri]


@jaclang_server.feature(TEXT_DOCUMENT_DEFINITION)
def definition(ls: JaclangLanguageServer, params: DefinitionParams):
    """Returns definition of a symbol."""
    doc = ls.workspace.get_document(params.text_document.uri)
    position = params.position
    print(doc.symbols, position)
    ls.show_message("Text Document Definition")
    return None


@jaclang_server.feature(
    TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    SemanticTokensLegend(token_types=["operator"], token_modifiers=[]),
)
def semantic_tokens(ls: JaclangLanguageServer, params: SemanticTokensParams):
    """See https://microsoft.github.io/language-server-protocol/specification#textDocument_semanticTokens
    for details on how semantic tokens are encoded."""

    TOKENS = re.compile('".*"(?=:)')

    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)

    last_line = 0
    last_start = 0

    data = []

    for lineno, line in enumerate(doc.lines):
        last_start = 0

        for match in TOKENS.finditer(line):
            start, end = match.span()
            data += [(lineno - last_line), (start - last_start), (end - start), 0, 0]

            last_line = lineno
            last_start = start

    return SemanticTokens(data=data)

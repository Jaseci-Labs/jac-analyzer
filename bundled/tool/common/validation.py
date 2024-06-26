from jaclang.compiler.passes.transform import Alert
from jaclang.compiler.parser import JacParser
from jaclang.compiler.absyntree import JacSource
from jaclang.compiler.passes.main import (
    SubNodeTabPass,
    JacImportPass,
    PyImportPass,
    SymTabBuildPass,
    DeclDefMatchPass,
    DefUsePass,
)

from lsprotocol.types import Diagnostic, DiagnosticSeverity, Position, Range
from pygls.server import LanguageServer


default_schedule = [
    SubNodeTabPass,
    JacImportPass,
    PyImportPass,
    SymTabBuildPass,
    DeclDefMatchPass,
    DefUsePass,
]


def jac_to_errors(
    file_path: str, source: str, schedule=default_schedule
) -> tuple[list[Alert], list[Alert]]:
    source = JacSource(source, file_path)
    prse = JacParser(source)
    for i in schedule:
        prse = i(input_ir=prse.ir, prior=prse)
    return prse.errors_had, prse.warnings_had


def validate(
    ls: LanguageServer, params: any, use_source: bool = False, rebuild: bool = False
) -> list[Diagnostic]:
    text_doc = ls.workspace.get_text_document(params.text_document.uri)
    source = text_doc.source
    doc_path = params.text_document.uri.replace("file://", "")
    diagnostics = (
        _validate_jac(ls, doc_path, source, use_source, rebuild) if source else []
    )
    return diagnostics


def _validate_jac(
    ls: LanguageServer,
    doc_path: str,
    source: str,
    use_source: bool = False,
    rebuild: bool = False,
) -> list[Diagnostic]:
    """
    Validate a JAC file.

    Args:
        doc_path (str): The path to the JAC file.
        source (str): The source code of the JAC file.
        use_source (bool, optional): Whether to use the source code to validate the JAC file. Defaults to False.
        rebuild (bool, optional): Whether to rebuild the JAC file. Defaults to False.

    Returns:
        list[Diagnostic]: A list of diagnostics for the JAC file.
    """
    diagnostics = []
    if use_source:
        errors, warnings = jac_to_errors(doc_path, source)
        if rebuild and len(errors) == 0:
            ls.jlws.rebuild_file(doc_path, False, source)
            errors, warnings = (
                ls.jlws.modules[doc_path].errors,
                ls.jlws.modules[doc_path].warnings,
            )
    else:
        if rebuild:
            ls.jlws.rebuild_file(doc_path)
        errors, warnings = (
            ls.jlws.modules[doc_path].errors,
            ls.jlws.modules[doc_path].warnings,
        )

    if not ls.settings.get("showWarning", False):
        warnings = []

    print(errors, warnings)

    for alert in errors + warnings:
        msg = alert.msg
        loc = alert.loc
        diagnostics.append(
            Diagnostic(
                range=Range(
                    start=Position(line=loc.first_line, character=loc.col_start),
                    end=Position(line=loc.last_line, character=loc.col_end),
                ),
                message=msg,
                severity=DiagnosticSeverity.Error
                if alert in errors
                else DiagnosticSeverity.Warning,
            )
        )
    return diagnostics

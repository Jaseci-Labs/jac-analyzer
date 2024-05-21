import * as vscode from "vscode";

export type JacDocument = vscode.TextDocument & { languageId: "jac" };
export type JacEditor = vscode.TextEditor & { document: JacDocument };

export function isJacDocument(document: vscode.TextDocument): document is JacDocument {
    return document.languageId === "rust" && document.uri.scheme === "file";
}

export function setContextValue(key: string, value: any): Thenable<void> {
    return vscode.commands.executeCommand("setContext", key, value);
}
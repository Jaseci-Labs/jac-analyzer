import * as vscode from 'vscode';
import * as lc from 'vscode-languageclient/node';

import { setContextValue } from './util';
import { Ctx } from './ctx';

const JAC_PROJECT_CONTEXT_NAME = 'inJacProject';

export interface JacAnalyzerExtensionApi {
    readonly client?: lc.LanguageClient;

    notifyJac(): Promise<void>;
}

export async function deactivate() {
    await setContextValue(JAC_PROJECT_CONTEXT_NAME, undefined);
}

export async function activate(context: vscode.ExtensionContext): Promise<JacAnalyzerExtensionApi> {
    const ctx = new Ctx(context, createCommands(), fetchWorkspace());
    const api = await activateServer(ctx).catch((err) => {
        void vscode.window.showErrorMessage(
            `Cannot activate jac extension: ${err.message}`,
        );
        throw err;
    
    });
    await setContextValue(JAC_PROJECT_CONTEXT_NAME, true);
    return
}

async function activateServer(ctx: Ctx): Promise<JacAnalyzerExtensionApi> {
    return
}
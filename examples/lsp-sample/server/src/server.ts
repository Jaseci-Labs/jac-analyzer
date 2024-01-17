import {
    createConnection,
    TextDocuments,
    Diagnostic,
    DiagnosticSeverity,
    ProposedFeatures,
    InitializeParams,
    TextDocumentPositionParams,
    TextDocumentSyncKind,
    InitializeResult,
    CompletionItem,
    CompletionList,
} from 'vscode-languageserver/node';

import { TextDocument } from 'vscode-languageserver-textdocument';
import * as WebSocket from 'ws';
import { spawn } from 'child_process';

const connection = createConnection(ProposedFeatures.all);
const documents: TextDocuments<TextDocument> = new TextDocuments(TextDocument);
let ws: WebSocket | null = null;
const childProcess = spawn('python', ['-u','child.py'], { stdio: ['pipe', 'pipe', 'pipe', 'ipc']});

connection.onInitialize((params: InitializeParams) => {
    const capabilities = params.capabilities;

    console.warn("Hello");
    // Perform any necessary setup here
    setupChildProcess();

    const result: InitializeResult = {
        capabilities: {
            textDocumentSync: TextDocumentSyncKind.Incremental,
        },
    };
    return result;
});

function setupChildProcess() {
    console.log("Child Process Starting !");
    
    try {
        if (!childProcess) {
            throw new Error('Child process not defined');
        }

        if (!childProcess.stdout) {
            throw new Error('childProcess.stdout is null');
        }

        childProcess.stdout.once('data', (data) => {
            console.log("MMM");
            const output = data.toString().trim();
            console.log(`Child process output: ${output}`);
            
            if (output === 'Child server listening on port 51734') {
                // Child process is ready, establish WebSocket connection after a delay
                setTimeout(() => {
                    setupWebSocketConnection();
                }, 1000); // Adjust the delay as needed
            } else {
                console.error('Unexpected output from child process');
            }
        });
    } catch (error) {
        console.error(`Error in setupChildProcess: ${error}`);
    }

    console.log("Child Process should have started!");
}

childProcess.on('error', (err) => {
    console.error('Error starting child process:', err);
});

childProcess.on('exit', (code, signal) => {
    console.log(`Child process exited with code ${code} and signal ${signal}`);

});

function setupWebSocketConnection() {
    ws = new WebSocket('ws://localhost:51734');
    console.log("Opening an web socket!");
    ws.on('open', () => {
        console.log('WebSocket connection established with child process');
    });
    ws.on('close', () => {
        console.log('WebSocket connection closed');
        process.exit();
    });
}

documents.onDidChangeContent((change) => {
    validateTextDocument(change.document);
});

documents.onDidOpen((event) => {
    const document = event.document;
    setupChildProcess();
    connection.sendNotification('window/showMessage', [`Text Document Did Open: ${document.uri}`]);
});

documents.onDidClose((event) => {
    console.log("Triggered!");
    const document = event.document;
    connection.sendNotification('window/showMessage', `Text Document Did Close`);
});

connection.onCompletion((_textDocumentPosition: TextDocumentPositionParams) => {
    const completions: CompletionItem[] = [
        { label: '"' },
        { label: '[' },
        { label: ']' },
        { label: '{' },
        { label: '}' },
    ];

    const completionList: CompletionList = {
        isIncomplete: false,
        items: completions,
    };

    return completionList;
});

async function validateTextDocument(textDocument: TextDocument): Promise<void> {
    const text = textDocument.getText();
    console.log(text);
    try {
        ws?.send(text);
    } catch (error) {
        console.warn(error instanceof Error ? error.message : error);
    }

    ws?.on('message', (message) => {
        try {
            const response = JSON.parse(message.toString());
            console.log(response);
            if (response.status === 'error') {
                console.log(response);
                const diagnostic: Diagnostic = {
                    severity: DiagnosticSeverity.Error,
                    range: {
                        start: { line: 0, character: 0 },
                        end: textDocument.positionAt(text.length) ,
                    },
                    message: `${response.message}`,
                };

                connection.sendDiagnostics({ uri: textDocument.uri, diagnostics: [diagnostic] });
            } else if (response.type === 'success') {
                connection.sendDiagnostics({ uri: textDocument.uri, diagnostics: [] });
            }
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    });

}
// Additional features from the Python code
connection.onDidChangeConfiguration((change) => {

});

connection.onRequest('countDownBlocking', () => {
    countDownBlocking();
});

connection.onRequest('countDownNonBlocking', () => {
    countDownNonBlocking();
});

function countDownBlocking() {
    for (let i = 10; i > 0; i--) {
        connection.sendNotification('window/showMessage', [`Counting down... ${i}`]);
        sleep(1000);
    }
}

async function countDownNonBlocking() {
    for (let i = 10; i > 0; i--) {
        connection.sendNotification('window/showMessage', [`Counting down... ${i}`]);
        await sleepAsync(1000);
    }
}


function sleep(ms: number) {
    Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

function sleepAsync(ms: number) {
    return new Promise((resolve) => {
        setTimeout(resolve, ms);
    });
}

documents.listen(connection);
connection.listen();

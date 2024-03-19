// .vscode-test.js
const { defineConfig } = require('@vscode/test-cli');

module.exports = defineConfig([
    {
        label: 'unitTests',
        files: 'out/test/**/*.test.js',
        version: 'insiders',
        workspaceFolder: `${__dirname}/examples`,
        mocha: {
            ui: 'tdd',
            timeout: 20000,
            color: true,
        }
    }
    // you can specify additional test configurations, too
]);

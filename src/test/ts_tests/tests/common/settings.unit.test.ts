// Copyright (c) Jaseci Labs. All rights reserved.
// Licensed under the MIT License.

import { assert } from 'chai';
import * as path from 'path';
import * as sinon from 'sinon';
import * as TypeMoq from 'typemoq';
import { Uri, WorkspaceConfiguration, WorkspaceFolder } from 'vscode';
import { EXTENSION_ROOT_DIR } from '../../../../common/constants';
import * as python from '../../../../common/python';
import { ISettings, getWorkspaceSettings } from '../../../../common/settings';
import * as vscodeapi from '../../../../common/vscodeapi';

// eslint-disable-next-line @typescript-eslint/naming-convention
const DEFAULT_SEVERITY: Record<string, string> = {
    error: 'Error',
    note: 'Information',
};

suite('Settings Tests', () => {
    suite('getWorkspaceSettings tests', () => {
        let getConfigurationStub: sinon.SinonStub;
        let getInterpreterDetailsStub: sinon.SinonStub;
        let getWorkspaceFoldersStub: sinon.SinonStub;
        let configMock: TypeMoq.IMock<WorkspaceConfiguration>;
        let pythonConfigMock: TypeMoq.IMock<WorkspaceConfiguration>;
        let workspace1: WorkspaceFolder = {
            uri: Uri.file(path.join(EXTENSION_ROOT_DIR, 'src', 'test', 'testWorkspace', 'workspace1')),
            name: 'workspace1',
            index: 0,
        };

        setup(() => {
            getConfigurationStub = sinon.stub(vscodeapi, 'getConfiguration');
            getInterpreterDetailsStub = sinon.stub(python, 'getInterpreterDetails');
            configMock = TypeMoq.Mock.ofType<WorkspaceConfiguration>();
            pythonConfigMock = TypeMoq.Mock.ofType<WorkspaceConfiguration>();
            getConfigurationStub.callsFake((namespace: string, uri: Uri) => {
                if (namespace.startsWith('mypy')) {
                    return configMock.object;
                }
                return pythonConfigMock.object;
            });
            getInterpreterDetailsStub.resolves({ path: undefined });
            getWorkspaceFoldersStub = sinon.stub(vscodeapi, 'getWorkspaceFolders');
            getWorkspaceFoldersStub.returns([workspace1]);
        });

        teardown(() => {
            sinon.restore();
        });

        test('Default Settings test', async () => {
            configMock
                .setup((c) => c.get('severity', DEFAULT_SEVERITY))
                .returns(() => DEFAULT_SEVERITY)
                .verifiable(TypeMoq.Times.atLeastOnce());
            configMock
                .setup((c) => c.get('importStrategy', 'useBundled'))
                .returns(() => 'useBundled')
                .verifiable(TypeMoq.Times.atLeastOnce());

            const settings: ISettings = await getWorkspaceSettings('mypy', workspace1);

            assert.deepStrictEqual(settings.cwd, workspace1.uri.fsPath);
            assert.deepStrictEqual(settings.importStrategy, 'useBundled');
            assert.deepStrictEqual(settings.interpreter, []);
            assert.deepStrictEqual(settings.severity, DEFAULT_SEVERITY);
            assert.deepStrictEqual(settings.workspace, workspace1.uri.toString());

            configMock.verifyAll();
            pythonConfigMock.verifyAll();
        });

        test('Resolver test', async () => {
            configMock
                .setup((c) => c.get('severity', DEFAULT_SEVERITY))
                .returns(() => DEFAULT_SEVERITY)
                .verifiable(TypeMoq.Times.atLeastOnce());
            configMock
                .setup((c) => c.get('importStrategy', 'useBundled'))
                .returns(() => 'useBundled')
                .verifiable(TypeMoq.Times.atLeastOnce());

            const settings: ISettings = await getWorkspaceSettings('mypy', workspace1, true);
            assert.deepStrictEqual(settings.interpreter, [
               
            ]);
            // TODO: Currently inteprater is defined manually, we have to find out how to configure it automatically
            // assert.deepStrictEqual(settings.interpreter, [
            //     `${process.env.HOME || process.env.USERPROFILE}/bin/python`,
            //     `${workspace1.uri.fsPath}/bin/python`,
            //     `${workspace1.uri.fsPath}/bin/python`,
            //     `${process.cwd()}/bin/python`,
            // ]);
            // assert.deepStrictEqual(settings.cwd, `${process.env.HOME || process.env.USERPROFILE}/bin`);

            configMock.verifyAll();
            pythonConfigMock.verifyAll();
        });
    });
});

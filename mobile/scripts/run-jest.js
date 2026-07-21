const { spawnSync } = require('node:child_process');

const nodeArguments = [];
if (process.allowedNodeEnvironmentFlags.has('--no-webstorage')) {
  nodeArguments.push('--no-webstorage');
}
nodeArguments.push(require.resolve('jest/bin/jest'), ...process.argv.slice(2));

const result = spawnSync(process.execPath, nodeArguments, { stdio: 'inherit' });
process.exit(result.status ?? 1);

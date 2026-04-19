const path = require("path");
const { spawnSync } = require("child_process");

const { resolvePythonCommand } = require("./python_command");

const rootDir = path.resolve(__dirname, "..");
const pythonCommand = resolvePythonCommand(rootDir);
const buildScript = path.join(__dirname, "build_backend.py");

const result = spawnSync(pythonCommand, [buildScript], {
  cwd: rootDir,
  stdio: "inherit",
  windowsHide: true,
});

if (result.error) {
  console.error(`Backend build failed to start: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status ?? 0);
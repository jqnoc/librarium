const fs = require("fs");
const path = require("path");

function resolvePythonCommand(rootDir) {
  const explicitPython = process.env.PYTHON;
  if (explicitPython) {
    return explicitPython;
  }

  const projectVenvPython = path.join(
    rootDir,
    ".venv",
    process.platform === "win32" ? "Scripts" : "bin",
    process.platform === "win32" ? "python.exe" : "python",
  );
  if (fs.existsSync(projectVenvPython)) {
    return projectVenvPython;
  }

  const activeVenv = process.env.VIRTUAL_ENV;
  if (activeVenv) {
    const activeVenvPython = path.join(
      activeVenv,
      process.platform === "win32" ? "Scripts" : "bin",
      process.platform === "win32" ? "python.exe" : "python",
    );
    if (fs.existsSync(activeVenvPython)) {
      return activeVenvPython;
    }
  }

  return process.platform === "win32" ? "python" : "python3";
}

module.exports = { resolvePythonCommand };
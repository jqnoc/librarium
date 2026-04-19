/**
 * Librarium — Electron main process
 *
 * Spawns the Flask backend as a child process, waits for it to become
 * ready, then opens the app in a frameless fullscreen BrowserWindow.
 */

const { app, BrowserWindow, dialog, ipcMain, shell } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const net = require("net");

const { resolvePythonCommand } = require("./scripts/python_command");

// ── State ────────────────────────────────────────────────────────────────
let mainWindow = null;
let splashWindow = null;
let flaskProcess = null;
let flaskPort = 0;
let isQuitting = false;
let quitRequest = null;

// ── Resolve paths (works both in dev and when packaged) ─────────────────
const isPackaged = app.isPackaged;
const assetRoot = __dirname;
const backendPath = isPackaged
  ? path.join(
      process.resourcesPath,
      "backend",
      process.platform === "win32" ? "librarium-backend.exe" : "librarium-backend",
    )
  : path.join(__dirname, "app.py");

// ── Port discovery ──────────────────────────────────────────────────────
const PREFERRED_PORT = 48720;

/**
 * Try to bind to PREFERRED_PORT first (keeps localStorage across restarts).
 * If it is already taken, fall back to an OS-assigned free port.
 */
function findFreePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.listen(PREFERRED_PORT, "127.0.0.1", () => {
      server.close(() => resolve(PREFERRED_PORT));
    });
    server.on("error", () => {
      // Preferred port taken — ask OS for any free port
      const fallback = net.createServer();
      fallback.listen(0, "127.0.0.1", () => {
        const port = fallback.address().port;
        fallback.close(() => resolve(port));
      });
      fallback.on("error", reject);
    });
  });
}

// ── Flask lifecycle ─────────────────────────────────────────────────────
function startFlask(port) {
  const env = {
    ...process.env,
    LIBRARIUM_PORT: String(port),
    LIBRARIUM_ELECTRON: "1",
    PYTHONIOENCODING: "utf-8",
  };

  const command = isPackaged ? backendPath : resolvePythonCommand(__dirname);
  const args = isPackaged ? [] : [backendPath];
  const cwd = isPackaged ? path.dirname(backendPath) : __dirname;

  flaskProcess = spawn(command, args, {
    cwd,
    env,
    stdio: "pipe",
    windowsHide: true,
  });

  flaskProcess.stdout.on("data", (data) => {
    console.log(`[Flask] ${data.toString().trim()}`);
  });

  flaskProcess.stderr.on("data", (data) => {
    console.log(`[Flask] ${data.toString().trim()}`);
  });

  flaskProcess.on("error", (err) => {
    console.error(`Failed to start Flask: ${err.message}`);
  });

  flaskProcess.on("close", (code) => {
    console.log(`Flask process exited with code ${code}`);
    flaskProcess = null;
  });
}

function killFlask() {
  if (!flaskProcess) return;
  if (process.platform === "win32") {
    // On Windows, child_process.kill() alone may not kill the tree.
    // Use taskkill to ensure the Python process and its children are stopped.
    spawn("taskkill", ["/pid", String(flaskProcess.pid), "/f", "/t"], {
      windowsHide: true,
    });
  } else {
    flaskProcess.kill("SIGTERM");
  }
  flaskProcess = null;
}

function hideShutdownOverlay() {
  if (!mainWindow || mainWindow.isDestroyed()) return;
  mainWindow.webContents
    .executeJavaScript(
      "var overlay = document.getElementById('shutdownOverlay'); if (overlay) overlay.style.display = 'none';",
      true,
    )
    .catch(() => {});
}

/**
 * Poll the Flask port until it accepts a TCP connection.
 * Retries up to `retries` times with `interval` ms between attempts.
 */
function waitForFlask(port, retries = 120, interval = 250) {
  return new Promise((resolve, reject) => {
    let attempt = 0;
    const check = () => {
      const socket = net.createConnection({ port, host: "127.0.0.1" }, () => {
        socket.destroy();
        resolve();
      });
      socket.on("error", () => {
        attempt++;
        if (attempt >= retries) {
          reject(new Error("Flask server did not start in time"));
        } else {
          setTimeout(check, interval);
        }
      });
    };
    check();
  });
}

// ── Window creation ─────────────────────────────────────────────────────
async function createWindow() {
  // Show splash screen immediately
  splashWindow = new BrowserWindow({
    width: 340,
    height: 360,
    frame: false,
    transparent: true,
    resizable: false,
    alwaysOnTop: true,
    skipTaskbar: false,
    title: "Librarium",
    icon: path.join(assetRoot, "static", "logo.png"),
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });
  splashWindow.loadFile(path.join(assetRoot, "static", "splash.html"));
  splashWindow.once("ready-to-show", () => splashWindow.show());

  try {
    flaskPort = await findFreePort();
    startFlask(flaskPort);
    await waitForFlask(flaskPort);
  } catch (err) {
    console.error(err.message);
    if (splashWindow) splashWindow.close();
    app.quit();
    return;
  }

  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 800,
    minHeight: 600,
    title: "Librarium",
    icon: path.join(assetRoot, "static", "logo.png"),
    backgroundColor: "#2a4a5a",
    show: false,
    frame: false,
    fullscreen: true,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      backgroundThrottling: false,
    },
  });

  mainWindow.loadURL(`http://127.0.0.1:${flaskPort}`);

  // Show window once the page has finished loading (avoids white flash)
  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
    if (splashWindow) {
      splashWindow.close();
      splashWindow = null;
    }
  });

  // Open external links in the default browser, not inside the app
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith("http") && !url.includes(`127.0.0.1:${flaskPort}`)) {
      shell.openExternal(url);
      return { action: "deny" };
    }
    return { action: "allow" };
  });

  mainWindow.on("close", (event) => {
    if (!isQuitting) {
      event.preventDefault();
      app.quit();
    }
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

// ── IPC handlers ────────────────────────────────────────────────────────
ipcMain.on("app-quit", () => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.close();
    return;
  }
  app.quit();
});

ipcMain.on("app-minimize", () => {
  if (mainWindow) mainWindow.minimize();
});

// ── App lifecycle ───────────────────────────────────────────────────────
app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (!isQuitting) {
    app.quit();
  }
});

app.on("before-quit", (event) => {
  if (!isQuitting) {
    event.preventDefault();
    void requestQuit();
  } else {
    killFlask();
  }
});

async function requestQuit() {
  if (quitRequest) return quitRequest;

  quitRequest = (async () => {
    const result = await shutdownAndSync();
    if (result.ok) {
      isQuitting = true;
      killFlask();
      app.exit(0);
      return true;
    }

    const response = await dialog.showMessageBox({
      type: "warning",
      buttons: ["Cancel", "Quit Anyway"],
      defaultId: 0,
      cancelId: 0,
      noLink: true,
      title: "Librarium",
      message: "Backup or Dropbox sync did not finish.",
      detail:
        `${result.error}\n\nChoose \"Cancel\" to keep Librarium open and try again, or \"Quit Anyway\" to exit without a confirmed sync.`,
    });

    if (response.response === 1) {
      isQuitting = true;
      killFlask();
      app.exit(0);
    }

    hideShutdownOverlay();
    return false;
  })();

  try {
    return await quitRequest;
  } finally {
    quitRequest = null;
  }
}

/**
 * Call the Flask shutdown-backup endpoint to create a backup and sync
 * all data to Dropbox before the app quits.  Times out after 30 seconds.
 */
async function shutdownAndSync() {
  if (!flaskPort) return { ok: true };
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 30000);
    const response = await fetch(`http://127.0.0.1:${flaskPort}/api/shutdown-backup`, {
      method: "POST",
      signal: controller.signal,
    });
    clearTimeout(timeout);
    let payload = null;
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }

    if (!response.ok || !payload || payload.ok !== true) {
      return {
        ok: false,
        error:
          payload?.error ||
          `Shutdown sync returned an unexpected response (${response.status}).`,
      };
    }

    return { ok: true };
  } catch (e) {
    return { ok: false, error: `Shutdown sync request failed: ${e.message}` };
  }
}

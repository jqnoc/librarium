/**
 * Librarium — Electron main process
 *
 * Spawns the Flask backend as a child process, waits for it to become
 * ready, then opens the app in a frameless fullscreen BrowserWindow.
 */

const { app, BrowserWindow, ipcMain, shell } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const net = require("net");

// ── State ────────────────────────────────────────────────────────────────
let mainWindow = null;
let splashWindow = null;
let flaskProcess = null;
let flaskPort = 0;

// ── Resolve paths (works both in dev and when packaged) ─────────────────
const isPackaged = app.isPackaged;
const appRoot = isPackaged
  ? path.join(process.resourcesPath, "app")
  : __dirname;

// ── Port discovery ──────────────────────────────────────────────────────
const PREFERRED_PORT = 48721;

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

  const pythonCmd = process.platform === "win32" ? "python" : "python3";

  flaskProcess = spawn(pythonCmd, [path.join(appRoot, "app.py")], {
    cwd: appRoot,
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

/**
 * Poll the Flask port until it accepts a TCP connection.
 * Retries up to `retries` times with `interval` ms between attempts.
 */
function waitForFlask(port, retries = 60, interval = 250) {
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
    icon: path.join(appRoot, "static", "favicon.ico"),
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });
  splashWindow.loadFile(path.join(appRoot, "static", "splash.html"));
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
    icon: path.join(appRoot, "static", "favicon.ico"),
    backgroundColor: "#1a1a2e",
    show: false,
    frame: false,
    fullscreen: true,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
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

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

// ── IPC handlers ────────────────────────────────────────────────────────
ipcMain.on("app-quit", () => {
  app.quit();
});

// ── App lifecycle ───────────────────────────────────────────────────────
app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  killFlask();
  app.quit();
});

app.on("before-quit", () => {
  killFlask();
});

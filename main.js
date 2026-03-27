/**
 * Librarium — Electron main process
 *
 * Spawns the Flask backend as a child process, waits for it to become
 * ready, then opens the app in a frameless-style BrowserWindow.
 */

const { app, BrowserWindow, Menu, shell } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const net = require("net");

// ── State ────────────────────────────────────────────────────────────────
let mainWindow = null;
let flaskProcess = null;
let flaskPort = 0;

// ── Resolve paths (works both in dev and when packaged) ─────────────────
const isPackaged = app.isPackaged;
const appRoot = isPackaged
  ? path.join(process.resourcesPath, "app")
  : __dirname;

// ── Port discovery ──────────────────────────────────────────────────────
function findFreePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.listen(0, "127.0.0.1", () => {
      const port = server.address().port;
      server.close(() => resolve(port));
    });
    server.on("error", reject);
  });
}

// ── Flask lifecycle ─────────────────────────────────────────────────────
function startFlask(port) {
  const env = {
    ...process.env,
    LIBRARIUM_PORT: String(port),
    LIBRARIUM_ELECTRON: "1",
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

// ── Application menu ────────────────────────────────────────────────────
function buildMenu() {
  const template = [
    {
      label: "Librarium",
      submenu: [
        {
          label: "Reload",
          accelerator: "CmdOrCtrl+R",
          click: () => mainWindow && mainWindow.reload(),
        },
        { type: "separator" },
        {
          label: "Quit",
          accelerator: "CmdOrCtrl+Q",
          click: () => app.quit(),
        },
      ],
    },
    {
      label: "Edit",
      submenu: [
        { role: "undo" },
        { role: "redo" },
        { type: "separator" },
        { role: "cut" },
        { role: "copy" },
        { role: "paste" },
        { role: "selectAll" },
      ],
    },
    {
      label: "View",
      submenu: [
        { role: "zoomIn" },
        { role: "zoomOut" },
        { role: "resetZoom" },
        { type: "separator" },
        { role: "togglefullscreen" },
      ],
    },
  ];
  return Menu.buildFromTemplate(template);
}

// ── Window creation ─────────────────────────────────────────────────────
async function createWindow() {
  try {
    flaskPort = await findFreePort();
    startFlask(flaskPort);
    await waitForFlask(flaskPort);
  } catch (err) {
    console.error(err.message);
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
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  Menu.setApplicationMenu(buildMenu());

  mainWindow.loadURL(`http://127.0.0.1:${flaskPort}`);

  // Show window once the page has finished loading (avoids white flash)
  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
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

// ── App lifecycle ───────────────────────────────────────────────────────
app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  killFlask();
  app.quit();
});

app.on("before-quit", () => {
  killFlask();
});

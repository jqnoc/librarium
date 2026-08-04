/**
 * Librarium — Electron preload script
 *
 * Runs in a sandboxed renderer context with contextIsolation enabled.
 * Exposes only what the renderer strictly needs via contextBridge.
 */

const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("librarium", {
  isElectron: true,
  quit: () => ipcRenderer.send("app-quit"),
  minimize: () => ipcRenderer.send("app-minimize"),
  toggleMaximize: () => ipcRenderer.send("app-toggle-maximize"),
  getWindowState: () => ipcRenderer.invoke("app-window-state"),
  onWindowStateChanged: (callback) => {
    if (typeof callback !== "function") return () => {};
    const listener = (_event, isMaximized) => callback(Boolean(isMaximized));
    ipcRenderer.on("window-state-changed", listener);
    return () => ipcRenderer.removeListener("window-state-changed", listener);
  },
});

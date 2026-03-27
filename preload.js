/**
 * Librarium — Electron preload script
 *
 * Runs in a sandboxed renderer context with contextIsolation enabled.
 * Exposes only what the renderer strictly needs via contextBridge.
 */

const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("librarium", {
  isElectron: true,
});

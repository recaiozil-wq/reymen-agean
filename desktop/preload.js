/**
 * ReYMeN Desktop — Preload Script
 * 
 * Electron contextBridge ile renderer'a guvenli API sunar.
 * Renderer -> preload -> ipcMain -> Python bridge akisi.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('reymen', {
    // ── Uygulama Bilgisi ──────────────────────────────────────
    platform: process.platform,
    version: process.env.npm_package_version || '1.0.0',

    // ── IPC Komutlari ─────────────────────────────────────────
    getStatus: () => ipcRenderer.invoke('get-status'),
    restartBackend: () => ipcRenderer.invoke('restart-backend'),

    // ── Pencere Kontrolu ──────────────────────────────────────
    minimize: () => ipcRenderer.send('window-minimize'),
    maximize: () => ipcRenderer.send('window-maximize'),
    close: () => ipcRenderer.send('window-close'),

    // ── Bildirimler ──────────────────────────────────────────
    onNotification: (callback) => {
        ipcRenderer.on('notification', (_event, data) => callback(data));
    },
    
    // ── Web UI Erisimi ────────────────────────────────────────
    getWebUiUrl: () => `http://localhost:8765`,
});

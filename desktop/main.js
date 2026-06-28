/**
 * ReYMeN Desktop — Electron Main Process
 * 
 * Python backend (web_ui.py) yönetimi, pencere, tepsi, IPC.
 * 
 * Calistirma:
 *   npm start          — production modu
 *   npm run dev         — gelistirme modu (devtools acik)
 * 
 * Derleme:
 *   npm run build       — Windows installer
 *   npm run build:portable — Windows portable (tek exe)
 */

const { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain, Notification } = require('electron');
const { spawn } = require('child_process');
const { exec } = require('child_process');
const util = require('util');
const execAsync = util.promisify(exec);
const path = require('path');
const Store = require('electron-store');

// ── Sabitler ──────────────────────────────────────────────────────────
const DEV_MODE = process.env.ELECTRON_DEV === '1';
const WEB_UI_PORT = 8765;
const WEB_UI_URL = `http://localhost:${WEB_UI_PORT}`;
const STORE = new Store({ defaults: { windowBounds: { width: 1024, height: 768 } } });

// ── Durum ─────────────────────────────────────────────────────────────
let mainWindow = null;
let tray = null;
let pythonProcess = null;
let pythonPath = null;  // findPython'dan bulunan yol
let isQuitting = false;

// ── 1. Python Backend Yonetimi ────────────────────────────────────────

async function findPython() {
  // Bilinen yollari dene, bulamazsa throw et.
  const candidates = [
    // 1. Bilinen 3.14 yolu
    path.join(process.env.LOCALAPPDATA, 'Python', 'PythonCore-3.14-64', 'python.exe'),
    // 2. Fallback — standart kurulum yollari
    path.join(process.env.LOCALAPPDATA, 'Programs', 'Python', 'Python314', 'python.exe'),
    'C:\\Python314\\python.exe',
    // 3. PATH'teki her ne varsa son care
    'python3.14',
    'python',
  ];

  for (const candidate of candidates) {
    try {
      const { stdout } = await execAsync(`"${candidate}" --version`);
      if (stdout.includes('3.14') || stdout.includes('3.1')) {
        console.log('[Desktop] Python bulundu:', candidate, stdout.trim());
        return candidate;
      }
    } catch {
      continue;
    }
  }

  throw new Error('Python 3.14+ bulunamadi');
}


async function startPythonBackend() {
    // python_bridge.py'yi background process olarak baslat.
    let pythonExe;
    try {
        pythonExe = await findPython();
        pythonPath = pythonExe;  // getStatus() icin sakla
    } catch (e) {
        console.error('[Desktop]', e.message);
        return false;
    }
    
    // python_bridge.py yolunu bul (asar + extraResources + dev fallback)
    const fs = require('fs');
    const path = require('path');
    let bridgePath = null;
    
    // Sira 1: __dirname (dev mode veya asarUnpack)
    const dirnamePath = path.join(__dirname, 'python_bridge.py');
    if (fs.existsSync(dirnamePath)) {
        bridgePath = dirnamePath;
    }
    
    // Sira 2: process.resourcesPath (extraResources)
    if (!bridgePath && process.resourcesPath) {
        const resPath = path.join(process.resourcesPath, 'python_bridge.py');
        if (fs.existsSync(resPath)) {
            bridgePath = resPath;
        }
    }
    
    // Sira 3: asarUnpacked (asarUnpack ile unpack edilmis)
    if (!bridgePath) {
        const asarUnpacked = (__dirname || '').replace('app.asar', 'app.asar.unpacked');
        const unpackedPath = path.join(asarUnpacked, 'python_bridge.py');
        if (fs.existsSync(unpackedPath)) {
            bridgePath = unpackedPath;
        }
    }
    
    // Sira 4: resources/ alti (manuel fix-builder-files.js ile kopyalanmis)
    if (!bridgePath && process.resourcesPath) {
        const manuelPath = path.join(process.resourcesPath, 'python_bridge.py');
        if (fs.existsSync(manuelPath)) {
            bridgePath = manuelPath;
        }
    }
    if (!fs.existsSync(bridgePath)) {
        console.error(`[Desktop] ✘ python_bridge.py bulunamadi. Denenen yollar:
  - ${path.join(__dirname, 'python_bridge.py')}
  - ${path.join(process.resourcesPath, 'python_bridge.py')}
  - ${path.join(__dirname.replace('app.asar', 'app.asar.unpacked'), 'python_bridge.py')}`);
        return false;
    }
    
    console.log(`[Desktop] Python bridge baslatiliyor: ${bridgePath}`);
    
    pythonProcess = spawn(pythonExe, [bridgePath], {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: {
            ...process.env,
            WEB_UI_PORT: '8765',
            REYMEN_DESKTOP: '1',
            PYTHONUNBUFFERED: '1',
        },
    });
    
    // stdout'tan hazir sinyali bekle
    pythonProcess.stdout.on('data', (data) => {
        const msg = data.toString();
        console.log(`[Backend] ${msg.trim()}`);
        if (msg.includes('Running on') || msg.includes('Uvicorn running')) {
            console.log('[Desktop] ✅ Python backend hazir!');
            if (mainWindow) {
                mainWindow.loadURL(WEB_UI_URL);
            }
        }
    });
    
    pythonProcess.stderr.on('data', (data) => {
        console.log(`[Backend:stderr] ${data.toString().trim()}`);
    });
    
    // — Watchdog: backend cozunce yeniden baslat —
    pythonProcess.on('exit', (code, signal) => {
        if (isQuitting) return;
        console.log(`[Desktop] ⚠️ Python backend cikti (kod: ${code}, sinyal: ${signal})`);
        console.log('[Desktop] 🔄 3 saniye sonra yeniden baslatiliyor...');
        setTimeout(async () => {
            if (!isQuitting) {
                // once backendi beklemeden window'da "yeniden baglaniyor" goster
                if (mainWindow) {
                    mainWindow.loadURL(`data:text/html,
                        <html><body style="display:flex;align-items:center;justify-content:center;
                        font-family:sans-serif;background:#1a1a2e;color:#e0e0e0;">
                        <h2>🔄 ReYMeN yeniden başlatılıyor...</h2></body></html>`);
                }
                // 500ms bekle — port'un release olmasini bekle (EADDRINUSE engeli)
                await new Promise(resolve => setTimeout(resolve, 500));
                await startPythonBackend();
            }
        }, 3000);
    });
    
    // Bekleme timeout — 15 sn sonra hala hazir degilse yine de yukle
    setTimeout(() => {
        if (mainWindow && mainWindow.webContents && mainWindow.webContents.getURL() !== WEB_UI_URL) {
            console.log('[Desktop] ⏱ Backend timeout, sayfa yine de yukleniyor...');
            mainWindow.loadURL(WEB_UI_URL);
        }
    }, 15000);
    
    return true;
}


// ── 2. Pencere Yonetimi ──────────────────────────────────────────────

function createWindow() {
    // Ana pencereyi olustur.
    const bounds = STORE.get('windowBounds');
    
    mainWindow = new BrowserWindow({
        width: bounds.width,
        height: bounds.height,
        x: bounds.x,
        y: bounds.y,
        minWidth: 800,
        minHeight: 600,
        title: 'ReYMeN',
        icon: path.join(__dirname, 'renderer', 'icon.png'),
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
            sandbox: false,
        },
        show: false,
        backgroundColor: '#1a1a2e',
    });
    
    // Pencere gosterilmeden once backend hazir mi kontrol et
    if (pythonProcess && pythonProcess.connected !== false) {
        mainWindow.loadURL(WEB_UI_URL);
    } else {
        // Backend henuz hazir degil — bekleme ekrani goster
        mainWindow.loadURL(`data:text/html,
            <html><body style="display:flex;align-items:center;justify-content:center;
            font-family:sans-serif;background:#1a1a2e;color:#e0e0e0;">
            <h2>⏳ ReYMeN başlatılıyor...</h2></body></html>`);
    }
    
    // Pencere hazir olunca goster
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        if (DEV_MODE) {
            mainWindow.webContents.openDevTools();
        }
    });
    
    // Pencere kapatilirken
    mainWindow.on('close', (e) => {
        if (!isQuitting) {
            e.preventDefault();
            // Tepsiye kucult (kapatma degil)
            mainWindow.hide();
        }
    });
    
    // Pencere boyutunu kaydet
    mainWindow.on('resize', () => {
        const bounds = mainWindow.getBounds();
        STORE.set('windowBounds', bounds);
    });
    
    mainWindow.on('move', () => {
        const bounds = mainWindow.getBounds();
        STORE.set('windowBounds', bounds);
    });
}


// ── 3. Sistem Tepsisi ────────────────────────────────────────────────

function createTray() {
    // Sistem tepsisi ikonu + menu.
    // 16x16 ikon (yoksa varsayilan)
    let icon;
    try {
        icon = nativeImage.createFromPath(path.join(__dirname, 'renderer', 'tray-icon.png'));
        if (icon.isEmpty()) throw new Error('empty');
    } catch (_) {
        // Varsayilan ikon — 16x16 yesil daire
        icon = nativeImage.createEmpty();
    }
    
    tray = new Tray(icon);
    tray.setToolTip('ReYMeN AI Agent');
    
    const contextMenu = Menu.buildFromTemplate([
        {
            label: '🪟 Pencereyi Goster',
            click: () => {
                if (mainWindow) {
                    mainWindow.show();
                    mainWindow.focus();
                }
            },
        },
        {
            label: '📊 Durum',
            click: () => {
                const status = getStatus();
                if (mainWindow) {
                    mainWindow.webContents.send('notification', {
                        title: 'ReYMeN Durum',
                        body: `Backend: ${status.backend}\nSure: ${status.uptime}`,
                    });
                }
            },
        },
        { type: 'separator' },
        {
            label: '🔁 Yeniden Baslat',
            click: () => restartBackend(),
        },
        { type: 'separator' },
        {
            label: '❌ Cikis',
            click: () => {
                isQuitting = true;
                if (tray) tray.destroy();
                app.quit();
            },
        },
    ]);
    
    tray.setContextMenu(contextMenu);
    tray.on('double-click', () => {
        if (mainWindow) {
            mainWindow.show();
            mainWindow.focus();
        }
    });
}


// ── 4. IPC Kanallari ─────────────────────────────────────────────────

ipcMain.handle('get-status', async () => {
    return getStatus();
});

ipcMain.handle('restart-backend', async () => {
    return restartBackend();
});

ipcMain.on('window-minimize', () => {
    if (mainWindow) mainWindow.minimize();
});

ipcMain.on('window-maximize', () => {
    if (mainWindow) {
        if (mainWindow.isMaximized()) {
            mainWindow.unmaximize();
        } else {
            mainWindow.maximize();
        }
    }
});

ipcMain.on('window-close', () => {
    if (mainWindow) mainWindow.hide();
});


// ── 5. Yardimci Fonksiyonlar ─────────────────────────────────────────

function getStatus() {
    // Backend ve uygulama durumunu dondur.
    const uptime = pythonProcess ? 
        Math.floor((Date.now() - (pythonProcess._startTime || Date.now())) / 1000) + 's' : 
        'durduruldu';
    
    return {
        backend: pythonProcess && pythonProcess.exitCode === null ? 'calisiyor' : 'durduruldu',
        uptime: uptime,
        port: WEB_UI_PORT,
        python: pythonPath || 'bulunamadi',
        version: app.getVersion(),
    };
}


async function restartBackend() {
    // Python backend'i durdurup yeniden baslat.
    if (pythonProcess) {
        pythonProcess.kill('SIGTERM');
        setTimeout(() => {
            if (pythonProcess && pythonProcess.exitCode === null) {
                pythonProcess.kill('SIGKILL');
            }
        }, 3000);
    }
    return await startPythonBackend();
}


// ── 6. Uygulama Yasam Dongusu ────────────────────────────────────────

// Tek instance kilidi
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
    app.quit();
} else {
    app.on('second-instance', () => {
        if (mainWindow) {
            if (mainWindow.isMinimized()) mainWindow.restore();
            mainWindow.show();
            mainWindow.focus();
        }
    });
}


app.whenReady().then(async () => {
    // Python backend'i baslat
    await startPythonBackend();
    
    // Pencereyi olustur
    createWindow();
    
    // Tepsiyi olustur
    createTray();
    
    // macOS: doktik'e tiklayinca pencere ac
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});


app.on('window-all-closed', () => {
    // Windows/Linux'ta tepside kal (cikis menusunden kapat)
    // macos'ta uygulamayi kapat
    if (process.platform === 'darwin') {
        app.quit();
    }
});


app.on('before-quit', () => {
    isQuitting = true;
    
    // Python backend'i temizle
    if (pythonProcess) {
        try {
            pythonProcess.kill('SIGTERM');
        } catch (_) {}
        pythonProcess = null;
    }
    
    // Tepsiyi temizle
    if (tray) {
        tray.destroy();
        tray = null;
    }
});


console.log('[Desktop] ✅ ReYMeN Desktop baslatildi');
console.log(`[Desktop] Port: ${WEB_UI_PORT}, DevMode: ${DEV_MODE}`);

/**
 * entry.tsx — ReYMeN TUI giriş noktası.
 *
 * 1. TTY kontrolü yapar — non-TTY ortamında hata verir.
 * 2. GatewayClient'ı başlatır (Python tui_gateway.entry alt süreci).
 * 3. React/Ink ile App bileşenini render eder.
 */

import path from 'path';
import { fileURLToPath } from 'url';
import React from 'react';
import { render } from 'ink';
import { GatewayClient } from './gatewayClient.js';
import { App } from './app.js';

// TTY kontrolü
if (!process.stdout.isTTY) {
  process.stderr.write(
    '[reymentui] Hata: Bu komut yalnızca bir TTY terminalinde çalışır.\n' +
    'Lütfen doğrudan bir terminal penceresinde başlatın.\n',
  );
  process.exit(1);
}

// Proje kök dizini: reymentui/../ → hermes_projesi
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const srcRoot = path.resolve(__dirname, '..', '..');

// Python yorumlayıcı: REYMEN_PYTHON env değişkeni veya 'python'
const pythonBin = process.env.REYMEN_PYTHON ?? 'python';

const client = new GatewayClient(srcRoot, pythonBin);

// Gateway'den gelen stderr'ı ekrana bas (hata ayıklama için)
client.on('stderr', (line: string) => {
  if (process.env.REYMEN_DEBUG) {
    process.stderr.write(`[gateway] ${line}`);
  }
});

client.on('exit', ({ code }: { code: number | null }) => {
  if (code !== 0 && code !== null) {
    process.stderr.write(`[reymentui] Gateway beklenmedik biçimde kapandı (kod=${code})\n`);
  }
});

// Temiz çıkış için SIGINT / SIGTERM
function onShutdown() {
  client.destroy();
  process.exit(0);
}
process.on('SIGINT', onShutdown);
process.on('SIGTERM', onShutdown);

// Ink ile render et
const { unmount } = render(
  <App client={client} />,
  {
    exitOnCtrlC: false, // Ctrl+C'yi App bileşeni yönetir
  },
);

// Uygulama kapanınca gateway'i de kapat
process.on('exit', () => {
  unmount();
  client.destroy();
});

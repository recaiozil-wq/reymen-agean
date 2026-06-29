'use strict';
const vscode = require('vscode');

function activate(context) {
    console.log('ReYMeN Agent aktif edildi');

    // Sohbet komutu
    let chatCmd = vscode.commands.registerCommand('reymen.chat', async () => {
        const panel = vscode.window.createWebviewPanel(
            'reymenChat',
            'ReYMeN Sohbet',
            vscode.ViewColumn.Beside,
            { enableScripts: true, retainContextWhenHidden: true }
        );
        panel.webview.html = getChatHtml();
        panel.webview.onDidReceiveMessage(async (msg) => {
            if (msg.type === 'chat') {
                const yanit = await reymenSoru(msg.text);
                panel.webview.postMessage({ type: 'response', text: yanit });
            }
        });
    });

    // Secili kodu sor
    let askCmd = vscode.commands.registerCommand('reymen.askSelection', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return vscode.window.showWarningMessage('Kod secili degil');
        const selection = editor.document.getText(editor.selection);
        if (!selection) return vscode.window.showWarningMessage('Kod secili degil');

        vscode.window.withProgress({ location: vscode.ProgressLocation.Notification, title: 'ReYMeN soruyor...' }, async () => {
            const yanit = await reymenSoru(selection + '\n---\nBu kodu acikla ve varsa hatalari goster.');
            vscode.window.showInformationMessage('ReYMeN yanitladi');
            // Yaniti output kanalinda goster
            const channel = vscode.window.createOutputChannel('ReYMeN');
            channel.clear();
            channel.appendLine('[ReYMeN]');
            channel.appendLine(yanit);
            channel.show();
        });
    });

    // Durum kontrol
    let statusCmd = vscode.commands.registerCommand('reymen.status', async () => {
        try {
            const url = vscode.workspace.getConfiguration('reymen').get('mcpUrl', 'http://localhost:9000');
            const resp = await fetch(url + '/health', { signal: AbortSignal.timeout(5000) });
            const data = await resp.json();
            vscode.window.showInformationMessage('ReYMeN: Bagli (' + url + ')');
        } catch {
            vscode.window.showErrorMessage('ReYMeN: Baglanti yok');
        }
    });

    context.subscriptions.push(chatCmd, askCmd, statusCmd);
}

// MCP uzerinden ReYMeN'e soru sor
async function reymenSoru(prompt) {
    const url = vscode.workspace.getConfiguration('reymen').get('mcpUrl', 'http://localhost:9000');
    try {
        const resp = await fetch(url + '/tools/call', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tool: 'reymen_soru',
                parameters: { prompt: prompt }
            }),
            signal: AbortSignal.timeout(30000)
        });
        const data = await resp.json();
        return data.content?.[0]?.text || JSON.stringify(data);
    } catch (e) {
        return 'Hata: ' + e.message;
    }
}

function getChatHtml() {
    return `<!DOCTYPE html>
<html lang="tr">
<head>
<style>
body { font-family: -apple-system, sans-serif; padding: 16px; background: #1e1e1e; color: #ddd; }
#messages { margin-bottom: 12px; max-height: 400px; overflow-y: auto; }
.msg { padding: 8px; margin: 4px 0; border-radius: 6px; }
.user { background: #2d2d2d; }
.bot { background: #1a3a5c; }
#input { width: 100%; padding: 8px; background: #2d2d2d; color: #ddd; border: 1px solid #444; border-radius: 4px; }
button { margin-top: 8px; padding: 8px 16px; background: #0078d4; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
</style>
</head>
<body>
<div id="messages"></div>
<input type="text" id="input" placeholder="ReYMeN\'e sor..." />
<button onclick="gonder()">Gonder</button>
<script>
const vscode = acquireVsCodeApi();
function gonder() {
    const input = document.getElementById('input');
    const text = input.value.trim();
    if (!text) return;
    addMsg(text, 'user');
    input.value = '';
    vscode.postMessage({ type: 'chat', text: text });
}
function addMsg(text, role) {
    const div = document.createElement('div');
    div.className = 'msg ' + role;
    div.textContent = text;
    document.getElementById('messages').appendChild(div);
}
window.addEventListener('message', e => {
    if (e.data.type === 'response') addMsg(e.data.text, 'bot');
});
document.getElementById('input').addEventListener('keydown', e => {
    if (e.key === 'Enter') gonder();
});
</script>
</body>
</html>`;
}

function deactivate() {}

module.exports = { activate, deactivate };

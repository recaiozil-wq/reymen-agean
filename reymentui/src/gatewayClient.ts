/**
 * GatewayClient — Python tui_gateway.entry ile JSON-RPC 2.0 iletişimi.
 *
 * Python süreci stdin/stdout üzerinden JSON-RPC kullanır:
 *   İstek  → {"jsonrpc":"2.0","id":1,"method":"...","params":{...}}\n
 *   Yanıt  → {"jsonrpc":"2.0","id":1,"result":{...}}\n
 *   Olay   → {"jsonrpc":"2.0","method":"event","params":{"type":"...","payload":{...}}}\n
 */

import { ChildProcess, spawn } from 'child_process';
import { EventEmitter } from 'events';
import { createInterface, Interface } from 'readline';
import * as path from 'path';

export interface GatewayEvent {
  type: string;
  payload: unknown;
}

export interface SessionInfo {
  id: string;
  title: string;
  created_at?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'tool';
  content: string;
  ts?: number;
}

export interface StatusData {
  session_id?: string;
  state?: string;
  model?: string;
  [key: string]: unknown;
}

type PendingRequest = {
  resolve: (value: unknown) => void;
  reject: (err: Error) => void;
  timer: ReturnType<typeof setTimeout>;
};

export class GatewayClient extends EventEmitter {
  private proc: ChildProcess;
  private rl: Interface;
  private pending = new Map<number, PendingRequest>();
  private nextId = 1;
  public ready = false;

  constructor(srcRoot: string, pythonBin = 'python') {
    super();

    this.proc = spawn(pythonBin, ['-m', 'tui_gateway.entry'], {
      cwd: srcRoot,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: {
        ...process.env,
        ReYMeN_PYTHON_SRC_ROOT: srcRoot,
        PYTHONUNBUFFERED: '1',
      },
    });

    this.rl = createInterface({ input: this.proc.stdout! });
    this.rl.on('line', (line) => this._handleLine(line));

    this.proc.stderr?.on('data', (chunk: Buffer) => {
      this.emit('stderr', chunk.toString());
    });

    this.proc.on('exit', (code, signal) => {
      this.emit('exit', { code, signal });
      for (const [id, req] of this.pending) {
        clearTimeout(req.timer);
        req.reject(new Error(`Gateway exited (code=${code})`));
        this.pending.delete(id);
      }
    });
  }

  private _handleLine(line: string): void {
    const trimmed = line.trim();
    if (!trimmed) return;

    let msg: Record<string, unknown>;
    try {
      msg = JSON.parse(trimmed) as Record<string, unknown>;
    } catch {
      return;
    }

    // JSON-RPC başarılı yanıt
    if (typeof msg.id === 'number' && 'result' in msg) {
      const req = this.pending.get(msg.id);
      if (req) {
        clearTimeout(req.timer);
        this.pending.delete(msg.id);
        req.resolve(msg.result);
      }
      return;
    }

    // JSON-RPC hata yanıtı
    if (typeof msg.id === 'number' && 'error' in msg) {
      const req = this.pending.get(msg.id);
      if (req) {
        clearTimeout(req.timer);
        this.pending.delete(msg.id);
        const err = msg.error as Record<string, unknown>;
        req.reject(new Error(String(err?.message ?? JSON.stringify(msg.error))));
      }
      return;
    }

    // Bildirim / olay
    if (msg.method === 'event' && typeof msg.params === 'object' && msg.params !== null) {
      const params = msg.params as Record<string, unknown>;
      const evType = String(params.type ?? '');

      if (evType === 'gateway.ready') {
        this.ready = true;
        this.emit('ready', params.payload);
        return;
      }

      this.emit('event', { type: evType, payload: params.payload } as GatewayEvent);
    }
  }

  /** Ham JSON-RPC isteği gönder. */
  call(method: string, params: Record<string, unknown> | unknown[] = {}): Promise<unknown> {
    return new Promise((resolve, reject) => {
      const id = this.nextId++;
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`RPC timeout: ${method}`));
      }, 30_000);

      this.pending.set(id, { resolve, reject, timer });

      const payload = JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n';
      this.proc.stdin!.write(payload, (err) => {
        if (err) {
          clearTimeout(timer);
          this.pending.delete(id);
          reject(err);
        }
      });
    });
  }

  // ── Yüksek seviye yardımcılar ──────────────────────────────────

  async createSession(): Promise<string> {
    const res = await this.call('session.create', {});
    return String((res as Record<string, unknown>)?.session_id ?? '');
  }

  async listSessions(): Promise<SessionInfo[]> {
    const res = await this.call('session.list', {});
    const rows = (res as Record<string, unknown>)?.sessions;
    return Array.isArray(rows) ? (rows as SessionInfo[]) : [];
  }

  async submitPrompt(sessionId: string, text: string): Promise<void> {
    await this.call('prompt.submit', { session_id: sessionId, text });
  }

  async getHistory(sessionId: string): Promise<ChatMessage[]> {
    const res = await this.call('session.history', { session_id: sessionId });
    const msgs = (res as Record<string, unknown>)?.messages;
    return Array.isArray(msgs) ? (msgs as ChatMessage[]) : [];
  }

  async getStatus(sessionId: string): Promise<StatusData> {
    const res = await this.call('session.status', { session_id: sessionId });
    return (res as StatusData) ?? {};
  }

  async interruptSession(sessionId: string): Promise<void> {
    await this.call('session.interrupt', { session_id: sessionId });
  }

  destroy(): void {
    this.proc.kill('SIGTERM');
  }
}

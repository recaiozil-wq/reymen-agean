/**
 * app.tsx — Ana TUI ekranı.
 *
 * Düzen:
 *   ┌─────────────┬──────────────────────────┐
 *   │ SessionList │        ChatBox           │
 *   │  (sol)      │        (sağ)             │
 *   └─────────────┴──────────────────────────┘
 *   │              CommandInput               │
 *   └─────────────────────────────────────────┘
 *   │              StatusBar                  │
 *   └─────────────────────────────────────────┘
 */

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Box, useApp, useInput } from 'ink';
import { GatewayClient, type ChatMessage, type GatewayEvent, type SessionInfo, type StatusData } from './gatewayClient.js';
import { ChatBox } from './components/ChatBox.js';
import { CommandInput } from './components/CommandInput.js';
import { SessionList } from './components/SessionList.js';
import { StatusBar } from './components/StatusBar.js';

interface AppProps {
  client: GatewayClient;
}

export function App({ client }: AppProps) {
  const { exit } = useApp();

  const [connected, setConnected] = useState(false);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [activeSessionId, setActiveSessionId] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState('');
  const [sessionState, setSessionState] = useState('idle');
  const [model, setModel] = useState('');
  const [busy, setBusy] = useState(false);

  const streamBufRef = useRef('');

  // Gateway hazır olduğunda oturum listesini çek
  useEffect(() => {
    client.on('ready', async () => {
      setConnected(true);
      try {
        const list = await client.listSessions();
        setSessions(list);
        if (list.length > 0) {
          await activateSession(list[0].id);
        }
      } catch {
        // sessiz geç
      }
    });

    client.on('event', (ev: GatewayEvent) => {
      handleGatewayEvent(ev);
    });

    client.on('exit', () => {
      setConnected(false);
      exit();
    });

    return () => {
      client.removeAllListeners();
    };
  }, []);

  const activateSession = useCallback(async (sid: string) => {
    setActiveSessionId(sid);
    setMessages([]);
    setStreaming('');
    streamBufRef.current = '';
    try {
      const hist = await client.getHistory(sid);
      setMessages(hist);
      const status = await client.getStatus(sid);
      setSessionState(status.state ?? 'idle');
      setModel(String(status.model ?? ''));
    } catch {
      // sessiz geç
    }
  }, [client]);

  const handleGatewayEvent = useCallback((ev: GatewayEvent) => {
    const payload = ev.payload as Record<string, unknown> | null;

    switch (ev.type) {
      case 'agent.token':
      case 'token': {
        const tok = String(payload?.token ?? payload?.text ?? '');
        streamBufRef.current += tok;
        setStreaming(streamBufRef.current);
        break;
      }

      case 'agent.response':
      case 'message.complete': {
        const content = String(payload?.content ?? streamBufRef.current ?? '');
        if (content) {
          setMessages((prev) => [...prev, { role: 'assistant', content }]);
        }
        streamBufRef.current = '';
        setStreaming('');
        setBusy(false);
        setSessionState('idle');
        break;
      }

      case 'session.status': {
        const st = String(payload?.state ?? '');
        if (st) setSessionState(st);
        const m = String(payload?.model ?? '');
        if (m) setModel(m);
        break;
      }

      case 'sessions.updated': {
        client.listSessions().then(setSessions).catch(() => undefined);
        break;
      }
    }
  }, [client]);

  const handleSubmit = useCallback(async (text: string) => {
    if (busy) return;

    let sid = activeSessionId;
    if (!sid) {
      try {
        sid = await client.createSession();
        setActiveSessionId(sid);
        const list = await client.listSessions();
        setSessions(list);
      } catch (err) {
        setMessages((prev) => [...prev, {
          role: 'assistant',
          content: `[Hata] Oturum oluşturulamadı: ${String(err)}`,
        }]);
        return;
      }
    }

    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setBusy(true);
    setSessionState('running');
    streamBufRef.current = '';

    try {
      await client.submitPrompt(sid, text);
    } catch (err) {
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: `[Hata] ${String(err)}`,
      }]);
      setBusy(false);
      setSessionState('idle');
    }
  }, [activeSessionId, busy, client]);

  const handleInterrupt = useCallback(async () => {
    if (activeSessionId && busy) {
      try {
        await client.interruptSession(activeSessionId);
      } catch {
        // sessiz geç
      }
      setBusy(false);
      setSessionState('idle');
    }
  }, [activeSessionId, busy, client]);

  // F5 → yeni oturum, Ctrl+C → çıkış (busy değilse)
  useInput(async (input, key) => {
    if (key.ctrl && input === 'c') {
      if (!busy) exit();
      return;
    }

    // Ctrl+N → yeni oturum
    if (key.ctrl && input === 'n') {
      try {
        const sid = await client.createSession();
        setActiveSessionId(sid);
        setMessages([]);
        const list = await client.listSessions();
        setSessions(list);
      } catch {
        // sessiz geç
      }
    }

    // Yukarı/aşağı ok → oturumlar arasında geçiş
    if (key.upArrow || key.downArrow) {
      if (sessions.length < 2) return;
      const idx = sessions.findIndex((s) => s.id === activeSessionId);
      const next = key.upArrow
        ? Math.max(0, idx - 1)
        : Math.min(sessions.length - 1, idx + 1);
      if (next !== idx) {
        await activateSession(sessions[next].id);
      }
    }
  });

  return (
    <Box flexDirection="column" height="100%">
      {/* Ana içerik */}
      <Box flexGrow={1} flexDirection="row">
        <SessionList
          sessions={sessions}
          activeId={activeSessionId}
        />
        <ChatBox messages={messages} streaming={streaming} />
      </Box>

      {/* Girdi satırı */}
      <CommandInput
        onSubmit={handleSubmit}
        onInterrupt={handleInterrupt}
        disabled={!connected}
        placeholder={connected ? 'Mesajınızı yazın…' : 'Gateway bağlantısı bekleniyor…'}
      />

      {/* Durum çubuğu */}
      <StatusBar
        sessionId={activeSessionId}
        state={sessionState}
        model={model}
        connected={connected}
      />
    </Box>
  );
}

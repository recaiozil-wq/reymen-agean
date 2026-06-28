import React from 'react';
import { Box, Text } from 'ink';

interface StatusBarProps {
  sessionId: string;
  state: string;
  model?: string;
  connected: boolean;
}

export function StatusBar({ sessionId, state, model, connected }: StatusBarProps) {
  const connColor = connected ? 'green' : 'red';
  const connLabel = connected ? '●' : '○';
  const stateColor = state === 'running' ? 'yellow' : state === 'idle' ? 'green' : 'gray';

  return (
    <Box borderStyle="single" borderColor="gray" paddingX={1}>
      <Text color={connColor}>{connLabel} </Text>
      <Text color="cyan">ReYMeN</Text>
      <Text color="gray"> │ </Text>
      {sessionId ? (
        <>
          <Text color="white">oturum: </Text>
          <Text color="yellow">{sessionId.slice(0, 8)}</Text>
          <Text color="gray"> │ </Text>
          <Text color={stateColor}>{state || 'bekleniyor'}</Text>
        </>
      ) : (
        <Text color="gray">oturum yok</Text>
      )}
      {model && (
        <>
          <Text color="gray"> │ </Text>
          <Text color="magenta">{model}</Text>
        </>
      )}
      <Box flexGrow={1} />
      <Text color="gray">Ctrl+C çıkış · Enter gönder · Ctrl+N yeni oturum</Text>
    </Box>
  );
}

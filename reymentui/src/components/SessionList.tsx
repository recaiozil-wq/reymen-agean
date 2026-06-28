import React from 'react';
import { Box, Text } from 'ink';
import type { SessionInfo } from '../gatewayClient.js';

interface SessionListProps {
  sessions: SessionInfo[];
  activeId: string;
  onSelect?: (id: string) => void;
}

export function SessionList({ sessions, activeId }: SessionListProps) {
  if (sessions.length === 0) {
    return (
      <Box flexDirection="column" width={24} borderStyle="single" borderColor="gray" padding={1}>
        <Text color="gray" dimColor>Oturum yok</Text>
        <Text color="gray" dimColor>F5: yeni oturum</Text>
      </Box>
    );
  }

  return (
    <Box flexDirection="column" width={24} borderStyle="single" borderColor="gray">
      <Box paddingX={1}>
        <Text color="cyan" bold>Oturumlar</Text>
      </Box>
      {sessions.map((s) => {
        const isActive = s.id === activeId;
        const title = s.title || s.id.slice(0, 8);
        return (
          <Box key={s.id} paddingX={1}>
            <Text
              color={isActive ? 'cyan' : 'white'}
              bold={isActive}
            >
              {isActive ? '▶ ' : '  '}
              {title.length > 18 ? title.slice(0, 18) + '…' : title}
            </Text>
          </Box>
        );
      })}
    </Box>
  );
}

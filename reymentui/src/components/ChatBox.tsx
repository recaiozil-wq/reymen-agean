import React from 'react';
import { Box, Text } from 'ink';
import type { ChatMessage } from '../gatewayClient.js';

interface ChatBoxProps {
  messages: ChatMessage[];
  streaming?: string;
}

export function ChatBox({ messages, streaming }: ChatBoxProps) {
  if (messages.length === 0 && !streaming) {
    return (
      <Box flexGrow={1} flexDirection="column" borderStyle="single" borderColor="gray" padding={1}>
        <Text color="gray" dimColor>
          ReYMeN ile konuşmak için mesaj yazın ve Enter'a basın.
        </Text>
      </Box>
    );
  }

  return (
    <Box flexGrow={1} flexDirection="column" borderStyle="single" borderColor="gray" padding={1} overflow="hidden">
      {messages.map((msg, i) => (
        <MessageRow key={i} msg={msg} />
      ))}
      {streaming && (
        <Box marginTop={1}>
          <Text color="cyan">▸ </Text>
          <Text color="white">{streaming}</Text>
          <Text color="yellow">█</Text>
        </Box>
      )}
    </Box>
  );
}

function MessageRow({ msg }: { msg: ChatMessage }) {
  if (msg.role === 'user') {
    return (
      <Box marginBottom={1}>
        <Text color="green" bold>Sen: </Text>
        <Text color="white">{msg.content}</Text>
      </Box>
    );
  }

  if (msg.role === 'assistant') {
    return (
      <Box marginBottom={1} flexDirection="column">
        <Text color="cyan" bold>ReYMeN: </Text>
        <Box paddingLeft={2}>
          <Text color="white">{msg.content}</Text>
        </Box>
      </Box>
    );
  }

  return (
    <Box marginBottom={1}>
      <Text color="gray" dimColor>[{msg.role}] {msg.content}</Text>
    </Box>
  );
}

import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';

interface CommandInputProps {
  onSubmit: (text: string) => void;
  onInterrupt?: () => void;
  disabled?: boolean;
  placeholder?: string;
}

export function CommandInput({ onSubmit, onInterrupt, disabled, placeholder }: CommandInputProps) {
  const [value, setValue] = useState('');
  const [cursor, setCursor] = useState(0);

  useInput((input, key) => {
    if (disabled) return;

    if (key.return) {
      const trimmed = value.trim();
      if (trimmed) {
        onSubmit(trimmed);
        setValue('');
        setCursor(0);
      }
      return;
    }

    if (key.ctrl && input === 'c') {
      onInterrupt?.();
      return;
    }

    if (key.backspace || key.delete) {
      if (cursor > 0) {
        setValue((v) => v.slice(0, cursor - 1) + v.slice(cursor));
        setCursor((c) => c - 1);
      }
      return;
    }

    if (key.leftArrow) {
      setCursor((c) => Math.max(0, c - 1));
      return;
    }

    if (key.rightArrow) {
      setCursor((c) => Math.min(value.length, c + 1));
      return;
    }

    // Ctrl+A → satır başı, Ctrl+E → satır sonu
    if (key.ctrl && input === 'a') {
      setCursor(0);
      return;
    }

    if (key.ctrl && input === 'e') {
      setCursor(value.length);
      return;
    }

    // Yazdırılabilir karakter
    if (input && !key.ctrl && !key.meta) {
      setValue((v) => v.slice(0, cursor) + input + v.slice(cursor));
      setCursor((c) => c + input.length);
    }
  });

  const before = value.slice(0, cursor);
  const atCursor = value[cursor] ?? ' ';
  const after = value.slice(cursor + 1);
  const showPlaceholder = !value && placeholder;

  return (
    <Box borderStyle="single" borderColor={disabled ? 'gray' : 'cyan'} paddingX={1}>
      <Text color={disabled ? 'gray' : 'green'} bold>{'>'} </Text>
      {showPlaceholder ? (
        <Text color="gray" dimColor>{placeholder}</Text>
      ) : (
        <>
          <Text color="white">{before}</Text>
          <Text color="black" backgroundColor="white">{atCursor}</Text>
          <Text color="white">{after}</Text>
        </>
      )}
    </Box>
  );
}

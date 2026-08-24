//JournalEntryCard.jsx


import { Card, Text, Group, Badge, Stack } from '@mantine/core';
import dayjs from 'dayjs';

const moodEmojis = {
  1: '😡',
  2: '😫',
  3: '😞',
  4: '😟',
  5: '😐',
  6: '🙂',
  7: '😄',
  8: '😃',
  9: '🤩',
  10: '🥳',
};

export default function JournalEntryCard({ entry }) {
  return (
    <Card shadow="sm" p="md" radius="md" withBorder style={{ backgroundColor: '#fff8f8' }}>
      <Text size="xs" c="gray" tt="capitalize" mb={4}>
        📅 {dayjs(entry.entry_date).format('dddd, MMM D')}
      </Text>

      <Group spacing="xs" mb="sm" align="center">
        <Badge color="pink" variant="light" size="lg" radius="xl">
          Mood {moodEmojis[entry.mood_score] || ''} {entry.mood_score}
        </Badge>
        <Badge color="violet" variant="light" size="lg" radius="xl">
          🏷️ {entry.mood_tag}
        </Badge>
      </Group>

      <Text size="sm" style={{ whiteSpace: 'pre-wrap', fontStyle: 'italic' }} c="dimmed">
        📝 {entry.notes || 'No additional notes.'}
      </Text>
    </Card>
  );
}



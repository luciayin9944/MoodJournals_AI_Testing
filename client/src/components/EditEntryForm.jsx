// EditEntryForm.jsx

import { useState } from 'react';
import { Textarea, Button, NumberInput, Select, Stack, Notification } from '@mantine/core';
import axios from 'axios';

const moodTags = [
    'Happy', 'Joyful', 'Excited', 'Relaxed', 'Calm',
    'Sad', 'Angry', 'Anxious', 'Stressed', 'Lonely','Productive', 
    'Tired', 'Overwhelmed', 'Bored', 'Disappointed','Nervous', 'Other'
];

export default function EditEntryForm({ entry, onUpdate }) {
  const [moodScore, setMoodScore] = useState(entry.mood_score);
  const [moodTag, setMoodTag] = useState(entry.mood_tag);
  const [notes, setNotes] = useState(entry.notes || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  
  const handleUpdate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.patch(`/entries/${entry.id}`, {
        mood_score: moodScore,
        mood_tag: moodTag,
        notes,
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (onUpdate) {
        onUpdate(res.data); 
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update entry.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack spacing="md" mt="md">
      {error && (
        <Notification color="red" onClose={() => setError(null)}>
          {error}
        </Notification>
      )}

      <NumberInput
        label="⭐ Mood Score (1-10)"
        value={moodScore}
        onChange={setMoodScore}
        min={1}
        max={10}
      />

      <Select
        label="🏷️ Mood Tag"
        data={moodTags}
        value={moodTag}
        onChange={setMoodTag}
        placeholder="Select your mood"
      />

      <Textarea
        label="📝 Notes"
        placeholder="Write your thoughts here..."
        value={notes}
        onChange={(e) => setNotes(e.currentTarget.value)}
        autosize
        minRows={4}
      />

      <Button loading={loading} onClick={handleUpdate}>
        Update Entry
      </Button>
    </Stack>
  );
}
// src/components/NewEntryForm.jsx

import { useState } from 'react';
import { Button, Textarea, NumberInput, Select, Stack, Group, Notification } from '@mantine/core';
import { DateInput } from '@mantine/dates';
import { useForm } from '@mantine/form';
import { IconX } from '@tabler/icons-react';
import dayjs from 'dayjs';
import axios from 'axios';


const moodTags = [
    'Happy', 'Joyful', 'Excited', 'Hopeful', 'Relaxed', 'Calm', 'Normal', 'Focused', 'Productive', 
    'Sad', 'Angry', 'Anxious', 'Stressed', 'Lonely', 'Worried', 'Tired', 'Overwhelmed', 'Bored', 'Disappointed', 'Nervous', 'Other'
];


export default function NewEntryForm({ defaultDate = new Date(), editableDate = true, onSuccess }) {
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState(null)

    const form = useForm({
        initialValues:{
            notes: "",
            mode_score: "",
            mood_tag:"Other",
            entry_date: defaultDate
        },
        validate: {
            notes: value => (value.length < 5 ? 'Notes must be at least 5 characters' : null),
            mood_score: value => (value < 1 || value > 10 ? 'Mood score must be between 1 and 10' : null),
            mood_tag: value => (!moodTags.includes(value) ? 'Invalid mood tag' : null),
        },
    });

    const handleSubmit = async values => {
        setSubmitting(true);
        setError(null);

    try {
      const payload = {
        notes: values.notes,
        mood_score: values.mood_score,
        mood_tag: values.mood_tag,
        entry_date: dayjs(values.entry_date).format('YYYY-MM-DD'),
      };

      const response = await axios.post('/entries', payload, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      form.reset();
      onSuccess?.(response.data);
    } catch (err) {
      setError(
        err.response?.data?.error || 'Failed to create entry.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={form.onSubmit(handleSubmit)}>
      <Stack spacing="sm">
        {editableDate && (
          <DateInput
            label="Entry Date"
            value={form.values.entry_date}
            onChange={date => form.setFieldValue('entry_date', date)}
            required
          />
        )}
        <Textarea
          label="📝 Notes"
          placeholder="What did you do or feel today?"
          minRows={2}
          required
          {...form.getInputProps('notes')}
        />
        <NumberInput
          label="⭐ Mood Score (1-10)"
          min={1}
          max={10}
          required
          {...form.getInputProps('mood_score')}
        />
        <Select
          label="🏷️ Mood Tag"
          data={moodTags}
          required
          {...form.getInputProps('mood_tag')}
        />

        {error && (
          <Notification color="red" icon={<IconX />} onClose={() => setError(null)}>
            {error}
          </Notification>
        )}

        <Group position="right">
          <Button type="submit" loading={submitting} >
            Add Entry
          </Button>
        </Group>
      </Stack>
    </form>
  );



    




}

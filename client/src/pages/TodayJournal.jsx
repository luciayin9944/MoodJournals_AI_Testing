// TodayJournal.jsx

import { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";
import axios from 'axios';
import {Title, Text, Card, Box, Loader, Button, Notification, Group, Container, Stack, Badge} from '@mantine/core';
import dayjs from 'dayjs'; 
import NewEntryForm from '../components/NewEntryForm';
import EditEntryForm from '../components/EditEntryForm';
import WeekEntriesGroup from '../components/WeekEntriesGroup';
import isoWeek from 'dayjs/plugin/isoWeek';
import weekOfYear from 'dayjs/plugin/weekOfYear';

dayjs.extend(isoWeek);
dayjs.extend(weekOfYear);

export default function TodayJournal() {
  const [todayEntry, setTodayEntry] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  const [journals, setJournals] = useState([]);
  const navigate = useNavigate();

  const currentWeek = dayjs().isoWeek();
  const currentYear = dayjs().year();

  const todayStr = dayjs().format('YYYY-MM-DD');

  const fetchTodayEntry = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`/entries/today`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setTodayEntry(res.data || null);
    } catch (err) {
      if (err.response?.status === 404) {
        setTodayEntry(null); // no entry = show create form
        setError(null);
      } else {
        setError(err.response?.data?.error || 'Failed to load entry.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTodayEntry();
  }, []);

  const handleDelete = async () => {
    try {
      await axios.delete(`/entries/${todayEntry.id}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setTodayEntry(null);
      setIsEditing(false);
      handleEntryChange();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete entry.');
    }
  };

  const fetchJournals = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`/journals`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setJournals(res.data.journals);
    } catch (err) {
      console.error('Failed to load journals', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJournals();
  }, []);

  const handleEntryChange = () => {
    fetchTodayEntry();
    fetchJournals();
  };

  if (loading) return <Loader mt="md" />;

  const currentWeekJournal = journals.find(j => j.year === currentYear && j.week_number === currentWeek);
  const startOfWeek = dayjs().year(currentYear).isoWeek(currentWeek).startOf('isoWeek');
  const endOfWeek = startOfWeek.endOf('isoWeek');
  const dateRangeStr = `${startOfWeek.format('MMMM D, YYYY')} - ${endOfWeek.format('MMMM D, YYYY')}`;

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

  return (
    <Container>
      <Box p="md">
        <Title order={1} mt={50} mb={20} ta="center">Your Mood Today</Title>
        <Text size="md" c="dimmed" ta="center" mb={40}>📅 {todayStr}</Text>

        {loading ? (
          <Loader mt="md" />
        ) : isEditing && todayEntry ? (
          <EditEntryForm
            entry={todayEntry}
            onUpdate={(updatedEntry) => {
              setTodayEntry(updatedEntry);
              setIsEditing(false);
              handleEntryChange();
            }}
          />
        ) : todayEntry ? (
          <Card mt="md" shadow="sm" padding="md" withBorder>
            {/* Mood + Tag */}
            <Group spacing="sm" mt="sm" mb="xl" align="center">
              <Badge color="pink" variant="filled" size="xl" radius="xl">
                Mood {moodEmojis[todayEntry.mood_score] || ''} {todayEntry.mood_score}
              </Badge>
              <Badge color="violet" variant="filled" size="xl" radius="xl">
                🏷️ {todayEntry.mood_tag}
              </Badge>
            </Group>
            <Text size="ml" style={{ whiteSpace: 'pre-wrap', fontStyle: 'italic' }} c="dimmed" mb="sm">
              📝 {todayEntry.notes || 'No additional notes.'}
            </Text>

            <Group position="right" spacing="xs">
              <Button color="blue" variant="outline" size="xs" onClick={() => setIsEditing(true)}>
                Edit
              </Button>
              <Button color="red" variant="outline" size="xs" onClick={handleDelete}>
                Delete
              </Button>
            </Group>
          </Card>
        ) : (
          <Box mt="md">
            <Text fw={700}>Oops, no entry found for today. Add one below:</Text>
            <NewEntryForm mt="lg"
              defaultDate={new Date()}
              editableDate={false}
              onSuccess={handleEntryChange}
            />
          </Box>
        )}

        {error && (
          <Notification color="red" onClose={() => setError(null)} mt="md">
            {error}
          </Notification>
        )}
      </Box>
      <Box mt="lg" mb={60}>
        <Stack>
          <Title order={3} mt={50} ta="center">Your Week in Moods</Title>
          <Text size="md" c="dimmed" ta="center" mb={30}>{dateRangeStr}</Text>
          {currentWeekJournal ? (
            <>
              <WeekEntriesGroup
                year={currentYear}
                week={currentWeek}
                expanded={true}
              />
              <Button onClick={() => navigate(`/journals/${currentYear}/${currentWeek}/summary`)}>
                View AI Insights
              </Button>
            </>
          ) : (
              <Text fw={700}>No journals for this week yet.</Text>
          )}
        </Stack>
      </Box>
    </Container>
  );
}


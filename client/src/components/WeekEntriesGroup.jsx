// // WeekEntriesGroup.jsx

import { useEffect, useState } from 'react';
import axios from 'axios';
import { Box, Text, Loader } from '@mantine/core';
import JournalEntryCard from './JournalEntryCard';

export default function WeekEntriesGroup({ year, week, expanded }) {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);

  const fetchEntries = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`/journals/${year}/${week}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setEntries(res.data);
      setHasLoaded(true);
    } catch (err) {
      console.error('Failed to load week entries', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (expanded && !hasLoaded) {
      fetchEntries();
    }
  }, [expanded, hasLoaded]);

  if (loading) return <Loader mt="sm" />;

  return (
    <Box mt="sm">
      {entries.map(entry => (
        <JournalEntryCard key={entry.id} entry={entry} />
      ))}
      {entries.length === 0 && <Text>No entries this week.</Text>}
    </Box>
  );
}






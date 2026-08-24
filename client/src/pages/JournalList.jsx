//JournalList.jsx

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Box, Title, Text, Stack, Button, Loader, Collapse, Flex, Pagination, Container, Paper, Group, Select } from '@mantine/core';
import WeekEntriesGroup from '../components/WeekEntriesGroup';
import dayjs from 'dayjs';
import isoWeek from 'dayjs/plugin/isoWeek';
import weekOfYear from 'dayjs/plugin/weekOfYear';

dayjs.extend(isoWeek);
dayjs.extend(weekOfYear);

export default function JournalList() {
  const navigate = useNavigate();
  const [journals, setJournals] = useState([]);
  const [expandedWeek, setExpandedWeek] = useState(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);

  const [selectedYear, setSelectedYear] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(null);
  const isFiltering = selectedYear && selectedYear !== 'all' && selectedMonth && selectedMonth !== 'all';


  const filteredJournals = journals.filter((j) => {
  if (selectedYear && selectedYear !== 'all') {
    if (!j.year) return false;
    if (j.year.toString() !== selectedYear) return false;
  }
  return true;
});


  const fetchJournals = async (pageNumber = 1) => {
    setLoading(true);
    try {
      const response = await axios.get(`/journals?page=${pageNumber}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setJournals(response.data.journals);
      setPages(response.data.pages);
      setPage(response.data.page);
    } catch (err) {
      console.error('Failed to load journals', err);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    fetchJournals();
  }, []);


  const handlePageChange = (newPage) => {
    fetchJournals(newPage);
  };

  const handleMonthFilter = async () => {
      if (!selectedYear || !selectedMonth) return;

      if (selectedMonth === 'all') {
        fetchJournals();  
        return;
      }
      setLoading(true);
      try {
        const response = await axios.get(`/entries/${selectedYear}/${selectedMonth}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        const journalEntries = response.data; 

        const groupedByWeek = journalEntries.reduce((acc, entry) => {
          const date = dayjs(entry.entry_date);
          const week = date.isoWeek();
          const year = date.year();
          const key = `${year}-W${week}`;

          if (!acc[key]) {
            acc[key] = { year, week_number: week, entries: [] };
          }
          acc[key].entries.push(entry);

          return acc;
        }, {});

        const sortedGroups = Object.entries(groupedByWeek).sort(([keyA], [keyB]) => {
          if (keyA === "All") return -1;
          if (keyB === "All") return 1;
          return 0;
        }).map(([, group]) => group)

        setJournals(sortedGroups);
      } catch (err) {
        console.error('Failed to filter by month:', err);
      } finally {
        setLoading(false);
      }
    };

  if (loading) return <Loader mt="md" />;

  const months = [
    { value: 'all', label: 'All' },
    { value: '1', label: 'January' },
    { value: '2', label: 'February' },
    { value: '3', label: 'March' },
    { value: '4', label: 'April' },
    { value: '5', label: 'May' },
    { value: '6', label: 'June' },
    { value: '7', label: 'July' },
    { value: '8', label: 'August' },
    { value: '9', label: 'September' },
    { value: '10', label: 'October' },
    { value: '11', label: 'November' },
    { value: '12', label: 'December' },
  ];


  return (
    <Container>
      <Box mt="lg" mb="xl">
        <Title order={1} mt={100} mb={30} ta="center">Your Journals</Title>

        <Flex justify="center" gap="md" mb="lg">
          <Select
            placeholder="Select year"
            data={[
              { label: 'All', value: 'all' },
              ...Array.from({ length: 3 }, (_, i) => {
                const year = dayjs().year() - i;
                return { label: year.toString(), value: year.toString() };
              }),
            ]}
            value={selectedYear}
            onChange={setSelectedYear}
            w={120}
          />
          <Select
            placeholder="Select month"
            data={months}
            value={selectedMonth}
            onChange={setSelectedMonth}
            w={150}
          />
          <Button onClick={handleMonthFilter}>Filter</Button>
        </Flex>
        <Stack>
            {filteredJournals.map(journal => {
                const weekKey = `${journal.year}-W${journal.week_number}`;
                const startOfWeek = dayjs().year(journal.year).week(journal.week_number).startOf('isoWeek');
                const endOfWeek = startOfWeek.endOf('isoWeek');

                const dateRangeStr = `${startOfWeek.format('MMMM D, YYYY')} - ${endOfWeek.format('MMMM D, YYYY')}`;   
                
            return (
                <Paper key={weekKey} shadow="xs" p="md" withBorder radius="md">
                  <Flex justify="space-between" align="center" mb="xs">
                    <Group position="apart" mb="xs">
                      <Button
                          variant={expandedWeek === weekKey ? 'filled' : 'outline'}
                          onClick={() =>
                              setExpandedWeek(prev => (prev === weekKey ? null : weekKey))
                          }
                          size="sm"
                      >
                      Week {journal.week_number}, {journal.year}
                      </Button>
                      <Text size="sm" c="dimmed">
                      {dateRangeStr}
                      </Text>
                    </Group>

                    <Button variant="light" onClick={() => navigate(`/journals/${journal.year}/${journal.week_number}/summary`)}>
                      Summary
                    </Button>
                  </Flex>

                  <Collapse in={expandedWeek === weekKey}>
                    <WeekEntriesGroup
                        year={journal.year}
                        week={journal.week_number}
                        expanded={expandedWeek === weekKey}
                    />
                  </Collapse>
                </Paper>
              );
            })}
        </Stack>
      </Box>
      
      {/* Pagination Controls */}
      {!isFiltering && (
        <Flex justify="center" mt={200} mb="xl">
          <Pagination
            total={pages}
            value={page}
            onChange={handlePageChange}
          />
        </Flex>
      )}
    </Container>
  );
}





// // Dashboard.jsx

import { useState } from 'react';
import {Box, Title, Text, Stack, Container, Slider, Group} from '@mantine/core';
import MonthlyWordCloud from '../components/MonthlyWordCloud';
import MonthlyMoodScores from '../components/MonthlyMoodScores';
import dayjs from 'dayjs';

export default function Dashboard({ user }) {
  const currentYear = dayjs().year();
  const currentMonth = dayjs().month() + 1; // month() is 0-indexed

  const [selectedMonth, setSelectedMonth] = useState(currentMonth);

  const monthLabels = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ];

  function handleMonthChange(value) {
    if (value <= currentMonth) {
      setSelectedMonth(value);
    }
  }

  return (
    <Container>
      <Text fw={700} mt={40} mb={30}>Welcome, {user.username}!</Text>

      <Stack>
        <Box>
          <Title order={1} ta="center" mb="xl">{currentYear}</Title>
          <Slider
            min={1}
            max={12}
            value={selectedMonth}
            onChange={handleMonthChange}
            step={1}
            marks={monthLabels.map((label, index) => ({
              value: index + 1,
              label,
            }))}
            mb="md"
          />
        </Box>
        <Box>
          <MonthlyWordCloud year={currentYear} month={selectedMonth} />
          <Title order={4} c="lightpink" mt={20} mb={40} ta="center">
            🔑 Your Mood Keywords in {monthLabels[selectedMonth - 1]}
          </Title>
        </Box>
        <Box>
          <MonthlyMoodScores year={currentYear} month={selectedMonth} />
          <Title order={4} c="lightpink" mt={20} mb={30} ta="center">
            📈 Your Mood Journey in {monthLabels[selectedMonth - 1]}
          </Title>
        </Box>
      </Stack>
    </Container>
  );
}



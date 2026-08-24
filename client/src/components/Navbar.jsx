// Navbar.jsx

import { Stack, Button } from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import { IconHome, IconNotes, IconRobot, IconNotebook } from '@tabler/icons-react';
import dayjs from 'dayjs';


export default function Navbar() {
  const navigate = useNavigate();

  const currentYear = dayjs().year();
  const currentWeek = dayjs().isoWeek();

  return (
    <Stack
      h={200}
      bg="var(--mantine-color-body)"
      align="stretch"
      justify="center"
      gap="xl"
      px="md"
      mt={50}
    >
      <Button
        variant="outline"
        color="grey"
        size="xl"
        onClick={() => navigate('/dashboard')}
        style={{ display: 'flex', alignItems: 'center', gap: 8 }}
      >
        <IconHome size={20} />
        Dashboard
      </Button>
      <Button
        variant="outline"
        color="grey"
        size="xl"
        onClick={() => navigate('/entries/today')}
        style={{ display: 'flex', alignItems: 'center', gap: 8 }}
      >
        <IconNotes size={20} />
        Current Journal
      </Button>
      <Button
        variant="outline"
        color="grey"
        size="xl"
        onClick={() => navigate(`/journals/${currentYear}/${currentWeek}/summary`)}
        style={{ display: 'flex', alignItems: 'center', gap: 8 }}
      >
        <IconRobot size={20} />
        Weekly AI Insights
      </Button>
      <Button
        variant="outline"
        color="grey"
        size="xl"
        onClick={() => navigate('/journals')}
        style={{ display: 'flex', alignItems: 'center', gap: 8 }}
      >
        <IconNotebook size={20} />
        All Journals
      </Button>
    </Stack>
  );
}
// MonthlyMoodScores.jsx

import { useEffect, useState } from "react";
import axios from "axios";
import { Container, Text, Loader, Alert, Box } from "@mantine/core";
import { IconAlertCircle } from "@tabler/icons-react";
import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartTooltip, ResponsiveContainer} from "recharts";
import dayjs from 'dayjs';

export default function MonthlyMoodScores({ year, month }) {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState([]);
  const allDates = getAllDaysInMonth(year, month);

  function getAllDaysInMonth(year, month) {
    const daysInMonth = dayjs(`${year}-${month}`).daysInMonth();
    return Array.from({ length: daysInMonth }, (_, i) => dayjs(`${year}-${month}-${i + 1}`).format('YYYY-MM-DD'));
  }

  useEffect(() => {
    const fetchEntries = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get(`/entries/${year}/${month}/analysis`, {
          headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        setData(response.data?.entries || []);
      } catch (err) {
                console.error(err);
                setError("Failed to fetch entries.");
      } finally {
          setIsLoading(false);
      }
    };
    fetchEntries();
  }, [year, month]);

  
  const moodScoreData = data?.map(entry => ({
    date: entry.entry_date,
    mood_score: entry.mood_score
  })) || [];

  const moodScoreMap = moodScoreData.reduce((acc, cur) => {
    acc[cur.date] = cur.mood_score;
    return acc;
  }, {});

  const completeChartData = allDates.map(date => ({
    date,
    mood_score: moodScoreMap[date] ?? null,
  }));

  const moodEmojiMap = {
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
    <Container size="md" mt="lg">
        {isLoading && <Loader />}
        {error && (
            <Alert icon={<IconAlertCircle />} color="red" mt="md">
            {error}
            </Alert>
        )}

        {!isLoading && data?.length > 0 && (
          <Box>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={completeChartData}>
                <XAxis 
                  dataKey="date" 
                  ticks={allDates} 
                  tickFormatter={(date) => dayjs(date).date()} 
                />
                <YAxis
                  domain={[1, 10]}
                  ticks={[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
                  tickFormatter={(value) => moodEmojiMap[value] || value}
                  interval={0}
                />
                <RechartTooltip labelFormatter={label => dayjs(label).format('MMM D')} />
                <Line dataKey="mood_score" stroke="#8884d8" strokeWidth={2} connectNulls />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        )}
    </Container> 
  );   
}
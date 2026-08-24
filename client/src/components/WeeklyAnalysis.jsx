// WeeklyAnalysis.jsx

import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { Container, Paper, Text, Loader, Alert, Title, Stack, Flex } from "@mantine/core";
import { IconAlertCircle } from "@tabler/icons-react";
import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartTooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend } from "recharts";

const COLORS = [
  "#8884d8", "#82ca9d", "#ffc658",
  "#ff8042", "#8dd1e1", "#d0ed57", "#a4de6c"
];

export default function WeeklyAnalysis() {
    const { year, week_number } = useParams();
    const [data, setData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);


    useEffect(() => {
        const fetchAnalysis = async () => {
            setIsLoading(true);
            try {
                const response = await axios.get(`/journals/${year}/${week_number}/analysis`, {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('token')}`,
                    },
                });
                setData(response.data.entries);
            } catch (err) {
                console.error(err);
                setError("Failed to fetch weekly analysis.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchAnalysis();
    }, [year, week_number]);


    const moodScoreData = data?.map(entry => ({
        date: entry.entry_date,
        mood_score: entry.mood_score
    }));

    const moodTagCounts = {};
    data?.forEach(entry => {
        moodTagCounts[entry.mood_tag] = (moodTagCounts[entry.mood_tag] || 0) + 1;
    });
    const moodTagData = Object.entries(moodTagCounts).map(([tag, count]) => ({
        name: tag,
        value: count
    }));

    return (
      <Container size="md" mt="lg">

        {isLoading && <Loader />}
        {error && (
            <Alert icon={<IconAlertCircle />} color="red" mt="md">
            {error}
            </Alert>
        )}

        {!isLoading && data && (
            <Flex gap="xl">
            {/* Mood Score Over Time */}
              <Paper withBorder shadow="sm" p="md" w={500} h={450}>
                <Title order={5} c="lightpink" mb="xl">📈 Mood Score Over Time</Title>
                <ResponsiveContainer width="100%" height={350}>
                  <LineChart data={moodScoreData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis domain={[1, 10]} />
                    <RechartTooltip />
                    <Line type="monotone" dataKey="mood_score" stroke="#8884d8" />
                  </LineChart>
                </ResponsiveContainer>
              </Paper>

            {/* Mood Tag Frequency */}
              <Paper withBorder shadow="sm" p="md" w={500} h={450}>
                <Title order={5} c="lightpink" mb="xl">📊 Mood Tag Frequency</Title>
                <ResponsiveContainer width="100%" height={350}>
                  <PieChart>
                    <Pie
                    data={moodTagData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                    >
                    {moodTagData.map((_, index) => (
                        <Cell key={index} fill={COLORS[index % COLORS.length]} />
                    ))}
                    </Pie>
                    <RechartTooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Paper>
            </Flex>
        )}
      </Container>    
    );
}
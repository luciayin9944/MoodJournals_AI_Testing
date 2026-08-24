// WeeklySummary.jsx

import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from 'axios';
import { Alert, Title, Text, Stack, Button, Loader, Flex, Container, Paper, Card} from '@mantine/core';
import AiSuggestionForm from "../components/AiSuggestionForm";
import WeeklyAnalysis from "../components/WeeklyAnalysis";
import dayjs from 'dayjs';


export default function WeeklySummary() {
    const [suggestion, setSuggestion] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showForm, setShowForm] = useState(false);
    const [hasEntries, setHasEntries] = useState(false);  

    const { year, week_number } = useParams();
    const navigate = useNavigate();

    const fetchSuggestion = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await axios.get(`/journals/${year}/${week_number}/suggestion`, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('token')}`,
                },
            })
            setSuggestion(response.data);
        } catch (err) {
            if (err.response && err.response.status === 404) {
                setSuggestion(null); // No suggestion yet
            } else {
                setError('Failed to load suggestion');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const checkIfEntriesExist = async () => {
        try {
            const response = await axios.get(`/journals/${year}/${week_number}/has_entries`, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('token')}`,
                },
            });
            setHasEntries(response.data.has_entries); // expects: { has_entries: true/false }
         } catch (err) {
            console.error('Failed to check journal entries', err);
        }
    };

    useEffect(() => {
        fetchSuggestion();
        checkIfEntriesExist();
    }, [year, week_number]);

    if (isLoading) {
    return <Loader mt="md" />;
  }

  const currentWeek = dayjs().isoWeek();
  const currentYear = dayjs().year();

  const startOfWeek = dayjs().year(currentYear).isoWeek(currentWeek).startOf('isoWeek');
  const endOfWeek = startOfWeek.endOf('isoWeek');
  const dateRangeStr = `${startOfWeek.format('MMMM D, YYYY')} - ${endOfWeek.format('MMMM D, YYYY')}`;


    return (
    <Container>
        <Title order={3} mt={50} mb={10} ta="center">Your Week's Highlights</Title>
        <Text size="md" c="dimmed" ta="center" mb={30}>{dateRangeStr}</Text>

        {hasEntries ? (
            <Stack>
                <Flex>
                    <WeeklyAnalysis year={year} week_number={week_number} />   
                </Flex>
            </Stack>
        ) : (
            <Stack align="center" mt={40} mb={60}>
                <Text size="md">Oops, no journal entry for this week yet.</Text>
                <Button variant="outline" onClick={() => navigate('/entries/today')}>Add Journal</Button>
            </Stack>
        )}

        <Stack mt={50}>
            <Title order={1} mt={30} mb="md" ta="center">AI Suggestions for You</Title>
            {error && <Alert color="red">{error}</Alert>}

            {suggestion && !showForm ? (
                <>
                  {(() => {
                    let parsedTips = [];

                    try {
                        parsedTips = JSON.parse(suggestion.selfcare_tips);
                    } catch (e) {
                        console.error('Failed to load suggestion', e);
                        parsedTips = suggestion.selfcare_tips.split('\n'); 
                    }

                    return (
                      <>
                        <Card shadow="sm" p="xl" withBorder radius="md" mb={20} style={{ backgroundColor: '#fff8f8' }}>
                            <Text fw={700} fz="lg" mb={10}> 📌 Summary</Text>
                            <Text>{suggestion.summary}</Text>
                        </Card>

                        <Card shadow="sm" p="xl" withBorder radius="md" mb={20} style={{ backgroundColor: '#fff8f8' }}>
                            <Text fw={700} fz="lg" mb={10}>💡 Self-Care Tips</Text>
                            <Stack>
                              {parsedTips.map((tip, index) => (
                                <Text key={index}>{tip.trim()}</Text>
                              ))}
                            </Stack>
                        </Card>
                      </>
                    );
                  })()}

                  {/* <Button variant="light" mb="xl" onClick={() => setShowForm(true)}>
                    🔄 Regenerate
                  </Button> */}
                </>
            ) : (
                <AiSuggestionForm
                    year={year}
                    week_number={week_number}
                    onSuccess={() => {
                        fetchSuggestion();
                        setShowForm(false); 
                    }}
                />       
            )}
        </Stack>
    </Container>
  );
}




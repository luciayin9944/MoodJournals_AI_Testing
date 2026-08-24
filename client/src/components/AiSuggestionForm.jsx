// AiSuggestionForm.jsx

import { useState } from "react";
import axios from "axios";
import { Button, Card, Text, List, Loader, Alert, Stack } from "@mantine/core";
import { IconAlertCircle } from "@tabler/icons-react";


export default function AiSuggestionForm({ year, week_number, onSuccess }) {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [summary, setSummary] = useState("")
    const [tips, setTips] = useState([]);
    
    const handleGenerate = async () => {
        setIsLoading(true);
        setError(null);
        setSummary("");
        setTips([]);

        try {
            const response = await axios.post(
            `/journals/${year}/${week_number}/suggestion`,
            {},  // POST body
            {
                headers: {
                Authorization: `Bearer ${localStorage.getItem("token")}`,
                },
            });
            const { summary, selfcare_tips } = response.data;

            let parsedTips;
            try {
                parsedTips = JSON.parse(selfcare_tips);  // parse JSON string to array
            } catch {
                parsedTips = selfcare_tips.split("\n");  // fallback in case it's raw text
            }
            setTips(parsedTips.filter((tip) => tip.trim()));
            setSummary(summary);
            
            if (onSuccess) {
                onSuccess();
            }
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.error || "Something went wrong.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Card shadow="sm" p="md" radius="md" withBorder style={{ backgroundColor: '#fff8f8' }}>
            {error && (
                <Alert icon={<IconAlertCircle size={16} />} color="red" mb="md">
                {error}
                </Alert>
            )}

            {isLoading ? (
                <Loader />
            ) : summary && summary.trim() ? (
              <>
                <Text fw={500}>📌 Summary</Text>
                <Text mb="md">{summary}</Text>

                <Text fw={500}>💡 Self-Care Tips</Text>
                <List>
                    {tips.map((tip, index) => (
                    <List.Item key={index}>{tip}</List.Item>
                    ))}
                </List>

                {/* <Button variant="light" mt="md" onClick={handleGenerate}>
                    🔄 Regenerate
                </Button> */}
              </>
            ) : (
              <Stack>
                <Text>No summary is available for this week.</Text>
                <Text size="sm" c="dimmed"> (A minimum of 4 journal entries is required to generate an AI-powered reflection.)</Text>
                <Button mt="xl" onClick={handleGenerate}>✨ Generate AI Suggestions</Button>
              </Stack>
            )}
        </Card>
    );

}

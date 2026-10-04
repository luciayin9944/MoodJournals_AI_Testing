// LongTermInsights.jsx

import { useState } from "react";
import axios from "axios";
import dayjs from "dayjs";
import { Alert, Badge, Button, Card, Container, Group, List, Stack, Text, Title, Select,} from "@mantine/core";
import { IconAlertCircle } from "@tabler/icons-react";


const questions = [
  "What situations usually make me feel anxious?",
  "What situations usually make me feel stressed?",
  "What tends to improve my mood?",
  "What situations usually make me feel happy?",
  "What tends to make me feel tired or overwhelmed?",
  "What recurring emotional patterns appear in my journal?",
  "What connections appear between my sleep and my mood?",
  "What connections appear between work and my mood?",
  "How do I tend to feel after spending time with other people?",
  "What activities do I mention when I feel calm or relaxed?",
  "How do I describe my mood after exercise or time outdoors?",
  "What has helped me cope during difficult days?",
];

const timeRanges = [
  { label: "3 Months", value: "3_months" },
  { label: "6 Months", value: "6_months" },
  { label: "1 Year", value: "1_year" },
  { label: "All Time", value: "all_time" },
];


export default function LongTermInsights() {
  const [question, setQuestion] = useState("");
  const [timeRange, setTimeRange] = useState("3_months");
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Send the selected question and range to the authenticated RAG endpoint.
  const handleAnalyze = async () => {
    if (!question || isLoading) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(
        "/analysis/long-term",
        { question, time_range: timeRange },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      setResult(response.data);
    } catch (err) {
      if (err.response?.status === 401 || err.response?.status === 422) {
        setError("Please sign in again to continue.");
      } else {
        setError(
          err.response?.data?.error || "Could not load your insights. Please try again."
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container pb="xl">
      <Title order={1} mt={50} mb={10} ta="center">
        Long-Term Insights
      </Title>
      <Text c="dimmed" ta="center" mb={30}>
        Explore patterns in your mood and the journal moments behind them.
      </Text>

      <Stack gap="xl">
        <Card shadow="sm" p="xl" radius="md" withBorder style={{ backgroundColor: "#fff8f8" }}>
          <Stack gap="lg">
            <Text fw={700} fz="lg">What would you like to explore?</Text>
            <Select
              placeholder="Select a question"
              data={questions}
              value={question || null}
              onChange={(value) => {
                setQuestion(value || "");
                setResult(null);
                setError(null);
              }}
              disabled={isLoading}
              clearable
              size="md"
              styles={{
                label: {
                  fontSize: "var(--mantine-font-size-lg)",
                  fontWeight: 700,
                  marginBottom: 12,
                },
              }}
            />

            <Text fw={700} fz="lg">Choose a time range</Text>
            <Group gap="sm">
              {timeRanges.map((range) => (
                <Button
                  key={range.value}
                  variant={timeRange === range.value ? "filled" : "outline"}
                  aria-pressed={timeRange === range.value}
                  disabled={isLoading}
                  onClick={() => {
                    setTimeRange(range.value);
                    setResult(null);
                    setError(null);
                  }}
                >
                  {range.label}
                </Button>
              ))}
            </Group>

            <Group justify="flex-end">
              <Button
                size="md"
                onClick={handleAnalyze}
                loading={isLoading}
                disabled={!question || isLoading}
              >
                Analyze
              </Button>
            </Group>
          </Stack>
        </Card>

        {isLoading && (
          <Text role="status" ta="center" c="dimmed">
            Looking through your journal and preparing your insights...
          </Text>
        )}

        {error && (
          <Alert icon={<IconAlertCircle size={18} />} color="red" title="Unable to load insights">
            {error}
          </Alert>
        )}

        {!result && !isLoading && !error && (
          <Text ta="center" c="dimmed">
            Choose a question, then select Analyze to explore your journal.
          </Text>
        )}

        {/* Empty sources and empty patterns have different meanings. */}
        {result && (
          result.sources.length === 0 ? (
            <Alert color="pink" title="Not enough journal evidence">
              <Text>{result.answer}</Text>
              <Text size="sm" mt="xs">
                Try a wider time range or add more journal entries.
              </Text>
            </Alert>
          ) : (
            <Stack gap="lg">
              <Card shadow="sm" p="xl" radius="md" withBorder style={{ backgroundColor: "#fff8f8" }}>
                <Text fw={700} fz="lg" mb="sm">📌 Your Reflection</Text>
                <Text style={{ whiteSpace: "pre-wrap" }}>{result.answer}</Text>
              </Card>

              <Card shadow="sm" p="xl" radius="md" withBorder style={{ backgroundColor: "#fff8f8" }}>
                <Text fw={700} fz="lg" mb="sm">💡 Recurring Patterns</Text>
                {result.patterns.length > 0 ? (
                  <List spacing="sm">
                    {result.patterns.map((pattern, index) => (
                      <List.Item key={index}>{pattern}</List.Item>
                    ))}
                  </List>
                ) : (
                  <Text c="dimmed">No recurring patterns identified in these entries.</Text>
                )}
              </Card>

              <Title order={2} size="h3" mt="sm">Supporting Journal Entries</Title>
              {result.sources.map((source) => (
                <Card key={source.entry_id} shadow="sm" p="md" radius="md" withBorder style={{ backgroundColor: "#fff8f8" }}>
                  <Text size="sm" c="dimmed" mb="sm">
                    📅 {dayjs(source.date).format("dddd, MMM D, YYYY")}
                  </Text>
                  <Group gap="xs" mb="sm">
                    <Badge color="pink" variant="light" size="lg">
                      Mood {source.mood_score}/10
                    </Badge>
                    <Badge color="violet" variant="light" size="lg">
                      {source.mood_tag}
                    </Badge>
                  </Group>
                  <Text size="sm" c="dimmed" style={{ whiteSpace: "pre-wrap", fontStyle: "italic" }}>
                    {source.notes || "No additional notes."}
                  </Text>
                </Card>
              ))}
            </Stack>
          )
        )}
      </Stack>
    </Container>
  );
}

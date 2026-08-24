// MonthlyWordCloud.jsx

import { useEffect, useState } from "react";
import axios from "axios";
import { Container, Box, Card, Text, Loader, Alert, Stack } from "@mantine/core";
import { IconAlertCircle } from "@tabler/icons-react";
import WordCloud from 'react-d3-cloud';

// const testData = [
//   { text: 'happy', value: 1000 },
//   { text: 'sad', value: 200 },
//   { text: 'excited', value: 800 },
// ];

const fontSizeMapper = word => Math.max(16, word.value * 5);

export default function MonthlyWordCloud({ year, month }) {

  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchWords = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get(`/entries/${year}/${month}/word_cloud`, {
          headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        console.log('Word cloud data:', response.data.word_cloud);
        
        const cleanedData = response.data.word_cloud
        .filter(({ text, value }) => text?.trim() && +value > 0)  
        .map(({ text, value }) => ({ 
          text: text.trim(), 
          value: +value * 1000  // enlarge value 
        }));

        setData(cleanedData);
      } catch (err) {
        console.error(err);
        setError("Failed to fetch words.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchWords();
  }, [year, month]);

  return (
    <Container size="md" mt="lg">
        {isLoading && <Loader />}
        {error && (
            <Alert icon={<IconAlertCircle />} color="red" mt="md">
            {error}
            </Alert>
        )}
        {!isLoading && data && (
          <Box
            shadow="xl"
            radius="xl"
            p="xl"
            w="100%"
            style={{
              border: "1px solid lightgray"
            }}
          >
            <WordCloud
              data={data}
              fontSizeMapper={fontSizeMapper}
              width={800}
              height={360}
            />
          </Box>
        )}
    </Container> 
  );
}
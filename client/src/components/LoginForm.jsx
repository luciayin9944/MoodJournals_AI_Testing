// src/components/LoginForm.jsx

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, TextInput, PasswordInput, Paper, Group, Button, Stack } from '@mantine/core';
import { useForm } from '@mantine/form';
import axios from 'axios';

export default function Login({ onLogin }) {
    const [isLoading, setIsLoading] = useState(false);
    const [errors, setErrors] = useState([]);
    const navigate = useNavigate();

    const form = useForm({
        initialValues:{
            email: '',
            password: ''
        }
    })

    const handleSubmit = async (values) => {
        setIsLoading(true);
        setErrors([]);
    
        try {
            const response = await axios.post('/login', {
                email: values.email,
                password: values.password
            });

            const { token, user } = response.data;
            onLogin(token, user);
            setIsLoading(false);
            navigate('/dashboard');
         } catch (error) {
            setIsLoading(false);

            if (error.response?.data?.errors) {
            setErrors(error.response.data.errors);
            } else {
            setErrors(['Login failed']);
            }
        }
    }

    return (
        <Paper shadow="md" radius="md" p="xl" withBorder maw={400} w="100%">
            <form onSubmit={form.onSubmit(handleSubmit)}>
                <Stack>
                    <TextInput
                        label="Email"
                        placeholder="your@email.com"
                        {...form.getInputProps('email')}
                        required
                    />
                    <PasswordInput
                        label="Password"
                        placeholder="Your password"
                        {...form.getInputProps('password')}
                        required
                    />
                </Stack>
                <Group justify="flex-end" mt="md">
                    <Button variant="light" type="submit" color="darkgreen" loading={isLoading}>Login</Button>
                </Group>
                
                {errors.length > 0 && (
                    <ul style={{ color: 'red' }}>
                    {errors.map((err, i) => <li key={i}>{err}</li>)}
                    </ul>
                )}
            </form>
        </Paper>
  
    )
}
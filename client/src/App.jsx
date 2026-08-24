// App.jsx

import React, { useEffect, useState } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";
import { AppShell, Button } from '@mantine/core';
import '@mantine/core/styles.css';
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/DashBoard.jsx";
import Header from "./components/Header.jsx";
import Navbar from "./components/Navbar.jsx";
import TodayJournal from "./pages/TodayJournal.jsx";
import axios from 'axios';
import JournalList from "./pages/JournalList.jsx";
import WeeklySummary from "./pages/WeeklySummary.jsx";


export default function App() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token")
    // console.log("token:", token);

    if (token) {
      axios.get('/me', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }).then((response) => {
        setUser(response.data)
      }).catch((err) => {
        console.log("Failed to fetch user:", err.response?.data || err.message);
      })
    }
  }, [])

  const onLogin = (token, user) => {
    localStorage.setItem("token", token);
    setUser(user);
    navigate("/dashboard")
  };
  
  if (!user) return <Login onLogin={onLogin} />;

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{ width: 300 }}
    >
      <AppShell.Header>
        <Header user={user} setUser={setUser} />
      </AppShell.Header>

      <AppShell.Navbar>
        <Navbar />
      </AppShell.Navbar>

      <AppShell.Main>
        <Routes>
          <Route path="/" element={<Login onLogin={onLogin} />} />
          <Route path="/dashboard" element={<Dashboard user={user} />} />
          <Route path="/entries/today" element={<TodayJournal />} />
          <Route path="/journals" element={<JournalList />} />
          <Route path="/journals/:year/:week_number/summary" element={<WeeklySummary />} />
          
        </Routes>
      </AppShell.Main>
    </AppShell>
  );
}


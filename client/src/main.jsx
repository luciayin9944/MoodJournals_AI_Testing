// main.jsx

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { createTheme, MantineProvider } from '@mantine/core'
import App from './App.jsx'


const theme= createTheme({
        fontFamily: 'Nunito, sans-serif',
        headings: { fontFamily: 'Nunito, sans-serif' },
        colors: {
          pastelPink: [
            '#fff0f6', '#ffdeeb', '#fcc2d7', '#faa2c1', '#f783ac',
            '#f06595', '#e64980', '#d6336c', '#c2255c', '#a61e4d'
          ],
          // pastelBlue: [
          //   '#e7f5ff', '#d0ebff', '#a5d8ff', '#74c0fc', '#4dabf7',
          //   '#339af0', '#228be6', '#1c7ed6', '#1971c2', '#1864ab'
          // ]
          brandGreen: [
            '#e6f4ea', 
            '#b3dfbb',
            '#80c98d',
            '#4db35e',
            '#27ae60', 
            '#1f8650',
            '#196c40',
            '#134d2c',
            '#0d321b',
            '#061909',
          ],
        },
        primaryColor: 'pastelPink',
        defaultRadius: 'lg',
        components: {
          Button: {
            styles: {
              root: {
                borderRadius: '999px', 
                fontWeight: 600,
                transition: 'transform 0.15s ease',
                '&:hover': {
                  transform: 'scale(1.05)',
                },
              },
            },
          },
          Card: {
            styles: {
              root: {
                borderRadius: '20px',
                boxShadow: '0 4px 15px rgba(255, 182, 193, 0.3)',
              },
            },
          },
          Title: {
            styles: {
              root: {
                color: '#ff69b4',
                fontWeight: 700,
              },
            },
          },
        },
      });

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <MantineProvider withGlobalStyles withNormalizeCSS theme={theme}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </MantineProvider>
  </StrictMode>
)




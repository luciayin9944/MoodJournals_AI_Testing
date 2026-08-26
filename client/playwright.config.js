import { defineConfig, devices } from '@playwright/test';
import { fileURLToPath } from 'node:url';
import path from 'node:path';


const clientDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(clientDir, '..');
const backendPython = path.join(rootDir, 'server', 'venv', 'bin', 'python');
const seedScript = path.join(rootDir, 'scripts', 'seed_test_data.py');
const e2eDatabaseUri = process.env.E2E_DATABASE_URI
  || 'sqlite:////tmp/moodjournal_e2e_test.db';

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://127.0.0.1:5173',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: [
    {
      command: `"${backendPython}" "${seedScript}" && "${backendPython}" -m flask --app run:app run --host=127.0.0.1 --port=5000`,
      cwd: path.join(rootDir, 'server'),
      url: 'http://127.0.0.1:5000/health',
      reuseExistingServer: false,
      timeout: 120_000,
      env: {
        ...process.env,
        DATABASE_URI: e2eDatabaseUri,
        E2E_DATABASE_URI: e2eDatabaseUri,
        JWT_SECRET_KEY: 'e2e-test-secret',
      },
    },
    {
      command: 'npm run dev -- --host 127.0.0.1',
      cwd: clientDir,
      url: 'http://127.0.0.1:5173',
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});

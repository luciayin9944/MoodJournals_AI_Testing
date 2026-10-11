import { expect, test } from './fixtures.js';

const endpoint = '**/analysis/long-term';
const question = 'What tends to improve my mood?';
const ranges = [
  ['3 Months', '3_months'],
  ['6 Months', '6_months'],
  ['1 Year', '1_year'],
  ['All Time', 'all_time'],
];

// Fixed API data keeps these browser tests independent of AI generation.
const analysis = {
  answer: 'Walking outdoors and talking with friends helped improve your mood.',
  patterns: ['Outdoor activities helped you relax.', 'Supportive conversations lifted your mood.'],
  sources: [
    {
      entry_id: 101,
      date: '2026-06-09',
      mood_tag: 'Relaxed',
      mood_score: 8,
      notes: 'A walk in the park helped me relax after work.',
    },
    {
      entry_id: 102,
      date: '2026-06-10',
      mood_tag: 'Happy',
      mood_score: 9,
      notes: 'Talking with a friend helped me feel supported.',
    },
  ],
};

async function openInsights(page) {
  await page.getByRole('button', { name: 'Long-term Insights', exact: true }).click();
  await expect(page).toHaveURL(/\/insights\/long-term$/);
  await expect(page.getByRole('heading', { name: 'Long-Term Insights', exact: true })).toBeVisible();
}

async function selectQuestion(page, value = question) {
  await page.getByPlaceholder('Select a question').click();
  await page.getByRole('option', { name: value, exact: true }).click();
}

async function mockAnalysis(page, response = analysis, status = 200) {
  await page.route(endpoint, (route) => route.fulfill({ status, json: response }));
}

test.beforeEach(async ({ page, loginAs }) => {
  await loginAs('ai');
  await openInsights(page);
});

test('requires a question', async ({ page }) => {
  await mockAnalysis(page);
  const requests = [];
  page.on('request', (request) => {
    if (request.url().endsWith('/analysis/long-term')) requests.push(request);
  });

  await expect(page.getByRole('button', { name: 'Analyze', exact: true })).toBeDisabled();
  await expect(page.getByRole('button', { name: '3 Months', exact: true })).toHaveAttribute('aria-pressed', 'true');
  await selectQuestion(page);
  await expect(page.getByRole('button', { name: 'Analyze', exact: true })).toBeEnabled();
  await page.getByRole('button', { name: 'Clear question', exact: true }).click();
  await expect(page.getByPlaceholder('Select a question')).toHaveValue('');
  await expect(page.getByRole('button', { name: 'Analyze', exact: true })).toBeDisabled();
  expect(requests).toHaveLength(0);
});

test('shows analysis', async ({ page }) => {
  await mockAnalysis(page);
  await selectQuestion(page);
  await page.getByRole('button', { name: 'All Time', exact: true }).click();

  const pendingRequest = page.waitForRequest(endpoint);
  await page.getByRole('button', { name: 'Analyze', exact: true }).click();
  const request = await pendingRequest;
  expect(request.method()).toBe('POST');
  expect(request.postDataJSON()).toEqual({ question, time_range: 'all_time' });
  // Compare without exposing the token in assertion output.
  const token = await page.evaluate(() => localStorage.getItem('token'));
  expect(Boolean(token) && request.headers().authorization === `Bearer ${token}`).toBe(true);

  await expect(page.getByText(analysis.answer, { exact: true })).toBeVisible();
  for (const pattern of analysis.patterns) {
    await expect(page.getByText(pattern, { exact: true })).toBeVisible();
  }
  await expect(page.getByRole('heading', { name: 'Supporting Journal Entries' })).toBeVisible();
  for (const source of analysis.sources) {
    await expect(page.getByText(source.notes, { exact: true })).toBeVisible();
    await expect(page.getByText(source.mood_tag, { exact: true })).toBeVisible();
    await expect(page.getByText(`Mood ${source.mood_score}/10`, { exact: true })).toBeVisible();
  }
  await expect(page.getByText('📅 Tuesday, Jun 9, 2026', { exact: true })).toBeVisible();
  await expect(page.getByText('📅 Wednesday, Jun 10, 2026', { exact: true })).toBeVisible();
});

for (const [label, value] of ranges) {
  test(`sends range: ${label}`, async ({ page }) => {
    await mockAnalysis(page);
    await selectQuestion(page);
    // Start from a different range so this also tests selecting the default again.
    await page.getByRole('button', { name: 'All Time', exact: true }).click();
    await page.getByRole('button', { name: label, exact: true }).click();
    await expect(page.getByRole('button', { name: label, exact: true })).toHaveAttribute('aria-pressed', 'true');
    const pendingRequest = page.waitForRequest(endpoint);
    await page.getByRole('button', { name: 'Analyze', exact: true }).click();
    expect((await pendingRequest).postDataJSON()).toEqual({ question, time_range: value });
    await expect(page.getByText(analysis.answer, { exact: true })).toBeVisible();
  });
}

test('shows loading', async ({ page }) => {
  let release;
  const pendingResponse = new Promise((resolve) => { release = resolve; });
  await page.route(endpoint, async (route) => {
    await pendingResponse;
    await route.fulfill({ json: analysis });
  });
  await selectQuestion(page);
  const pendingRequest = page.waitForRequest(endpoint);
  try {
    await page.getByRole('button', { name: 'Analyze', exact: true }).click();
    await pendingRequest;
    await expect(page.getByRole('status')).toHaveText('Looking through your journal and preparing your insights...');
    await expect(page.getByRole('button', { name: 'Analyze', exact: true })).toBeDisabled();
    await expect(page.getByPlaceholder('Select a question')).toBeDisabled();
    for (const [label] of ranges) {
      await expect(page.getByRole('button', { name: label, exact: true })).toBeDisabled();
    }
  } finally {
    // Release only after checking loading, without an arbitrary sleep.
    release();
  }
  await expect(page.getByText(analysis.answer, { exact: true })).toBeVisible();
  await expect(page.getByRole('status')).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Analyze', exact: true })).toBeEnabled();
  await expect(page.getByPlaceholder('Select a question')).toBeEnabled();
  for (const [label] of ranges) {
    await expect(page.getByRole('button', { name: label, exact: true })).toBeEnabled();
  }
});

test('shows insufficient evidence', async ({ page }) => {
  const answer = 'There is not enough journal evidence to answer this question.';
  await mockAnalysis(page, { answer, patterns: [], sources: [] });
  await selectQuestion(page);
  await page.getByRole('button', { name: 'Analyze', exact: true }).click();
  await expect(page.getByText('Not enough journal evidence', { exact: true })).toBeVisible();
  await expect(page.getByText(answer, { exact: true })).toBeVisible();
  await expect(page.getByText('Try a wider time range or add more journal entries.')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Supporting Journal Entries' })).toHaveCount(0);
});

test('shows no patterns', async ({ page }) => {
  await mockAnalysis(page, { ...analysis, patterns: [] });
  await selectQuestion(page);
  await page.getByRole('button', { name: 'Analyze', exact: true }).click();
  await expect(page.getByText(analysis.answer, { exact: true })).toBeVisible();
  await expect(page.getByText('No recurring patterns identified in these entries.')).toBeVisible();
  await expect(page.getByText('Not enough journal evidence', { exact: true })).toHaveCount(0);
  for (const source of analysis.sources) {
    await expect(page.getByText(source.notes, { exact: true })).toBeVisible();
  }
});

for (const [status, error] of [
  [500, 'Could not complete the analysis.'],
  [502, 'AI service could not complete the analysis.'],
  [504, 'AI service timed out. Please try again.'],
]) {
  test(`shows API error: ${status}`, async ({ page }) => {
    await mockAnalysis(page, { error }, status);
    await selectQuestion(page);
    await page.getByRole('button', { name: 'Analyze', exact: true }).click();
    await expect(page.getByRole('alert')).toContainText(error);
    await expect(page.getByRole('button', { name: 'Analyze', exact: true })).toBeEnabled();
    await expect(page.getByRole('status')).toHaveCount(0);
    await expect(page.getByRole('heading', { name: 'Supporting Journal Entries' })).toHaveCount(0);
  });
}

test('retries after an error', async ({ page }) => {
  let attempts = 0;
  await page.route(endpoint, (route) => {
    attempts += 1;
    return route.fulfill(attempts === 1
      ? { status: 504, json: { error: 'AI service timed out. Please try again.' } }
      : { json: analysis });
  });
  await selectQuestion(page);
  await page.getByRole('button', { name: 'Analyze', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText('AI service timed out. Please try again.');
  await page.getByRole('button', { name: 'Analyze', exact: true }).click();
  await expect(page.getByText(analysis.answer, { exact: true })).toBeVisible();
  await expect(page.getByRole('alert')).toHaveCount(0);
  expect(attempts).toBe(2);
});

for (const status of [401, 422]) {
  test(`shows sign-in error: ${status}`, async ({ page }) => {
    await mockAnalysis(page, { msg: 'Invalid authentication token.' }, status);
    await selectQuestion(page);
    await page.getByRole('button', { name: 'Analyze', exact: true }).click();
    await expect(page.getByRole('alert')).toContainText('Please sign in again to continue.');
    await expect(page.getByRole('button', { name: 'Analyze', exact: true })).toBeEnabled();
  });
}

for (const field of ['question', 'range']) {
  test(`clears results on ${field} change`, async ({ page }) => {
    await mockAnalysis(page);
    await selectQuestion(page);
    await page.getByRole('button', { name: 'Analyze', exact: true }).click();
    await expect(page.getByText(analysis.answer, { exact: true })).toBeVisible();
    if (field === 'question') {
      await selectQuestion(page, 'What connections appear between work and my mood?');
    } else {
      await page.getByRole('button', { name: '1 Year', exact: true }).click();
    }
    await expect(page.getByText(analysis.answer, { exact: true })).toHaveCount(0);
    await expect(page.getByRole('heading', { name: 'Supporting Journal Entries' })).toHaveCount(0);
    await expect(page.getByText('Choose a question, then select Analyze to explore your journal.')).toBeVisible();
  });
}

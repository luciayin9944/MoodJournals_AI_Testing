import { expect, test } from './fixtures.js';


test('user can generate and view a mocked AI suggestion', async ({ page, loginAs }) => {
  const suggestion = {
    summary: 'The week improved as stress gave way to hope, productivity, and rest.',
    selfcare_tips: JSON.stringify([
      'Keep breaking work into manageable steps.',
      'Protect time for rest after demanding tasks.',
      'Notice and record signs of progress.',
    ]),
  };
  let generated = false;

  await page.route('**/journals/*/*/suggestion', async (route) => {
    const method = route.request().method();
    if (method === 'POST') {
      generated = true;
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify(suggestion),
      });
      return;
    }
    if (method === 'GET' && generated) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(suggestion),
      });
      return;
    }
    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'No suggestion found for this week.' }),
    });
  });

  await loginAs('ai');
  await page.getByRole('button', { name: 'Weekly AI Insights' }).click();
  await expect(page.getByText('No summary is available for this week.')).toBeVisible();

  await page.getByRole('button', { name: '✨ Generate AI Suggestions' }).click();

  await expect(page.getByText(suggestion.summary)).toBeVisible();
  await expect(page.getByText('Keep breaking work into manageable steps.')).toBeVisible();
  await expect(page.getByText('Protect time for rest after demanding tasks.')).toBeVisible();
  await expect(page.getByText('Notice and record signs of progress.')).toBeVisible();
});

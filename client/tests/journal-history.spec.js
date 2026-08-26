import { expect, test } from './fixtures.js';


test('user can navigate to journal history and expand a week', async ({ page, loginAs }) => {
  await loginAs('history');
  await page.getByRole('button', { name: 'All Journals' }).click();

  await expect(page.getByRole('heading', { name: 'Your Journals' })).toBeVisible();
  await page.getByRole('button', { name: /^Week \d+, \d{4}$/ }).first().click();
  await expect(page.getByText('Current week history entry.')).toBeVisible();
});


test('user can filter journal history by current year and month', async ({ page, loginAs }) => {
  const now = new Date();
  const year = String(now.getFullYear());
  const month = now.toLocaleString('en-US', { month: 'long' });

  await loginAs('history');
  await page.getByRole('button', { name: 'All Journals' }).click();

  await page.getByPlaceholder('Select year').click();
  await page.getByRole('option', { name: year, exact: true }).click();
  await page.getByPlaceholder('Select month').click();
  await page.getByRole('option', { name: month, exact: true }).click();
  await page.getByRole('button', { name: 'Filter' }).click();

  await expect(page.getByRole('button', { name: /^Week \d+, \d{4}$/ }).first()).toBeVisible();
});

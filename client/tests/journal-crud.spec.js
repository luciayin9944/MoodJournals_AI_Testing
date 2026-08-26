import { expect, test } from './fixtures.js';


test('user can create today journal entry', async ({ page, loginAs }) => {
  await loginAs('create');
  await page.getByRole('button', { name: 'Current Journal' }).click();

  await expect(page.getByText('Oops, no entry found for today.')).toBeVisible();
  await page.getByLabel('📝 Notes').fill('Created through the Playwright browser flow.');
  await page.getByLabel('⭐ Mood Score (1-10)').fill('8');
  await page.getByLabel('🏷️ Mood Tag').click();
  await page.getByRole('option', { name: 'Happy', exact: true }).click();
  await page.getByRole('button', { name: 'Add Entry' }).click();

  await expect(page.getByText('Created through the Playwright browser flow.').first()).toBeVisible();
  await expect(page.getByText('🏷️ Happy', { exact: true }).first()).toBeVisible();
});


test('user can edit today journal entry', async ({ page, loginAs }) => {
  await loginAs('edit');
  await page.getByRole('button', { name: 'Current Journal' }).click();
  await expect(page.getByText('Original entry for editing.').first()).toBeVisible();

  await page.getByRole('button', { name: 'Edit' }).click();
  await page.getByLabel('⭐ Mood Score (1-10)').fill('9');
  await page.getByLabel('🏷️ Mood Tag').click();
  await page.getByRole('option', { name: 'Joyful', exact: true }).click();
  await page.getByLabel('📝 Notes').fill('Updated through the Playwright browser flow.');
  await page.getByRole('button', { name: 'Update Entry' }).click();

  await expect(page.getByText('Updated through the Playwright browser flow.').first()).toBeVisible();
  await expect(page.getByText(/Mood .* 9/).first()).toBeVisible();
});


test('user can delete today journal entry', async ({ page, loginAs }) => {
  await loginAs('delete');
  await page.getByRole('button', { name: 'Current Journal' }).click();
  await expect(page.getByText('Entry that will be deleted.').first()).toBeVisible();

  await page.getByRole('button', { name: 'Delete' }).click();

  await expect(page.getByText('Oops, no entry found for today.')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Add Entry' })).toBeVisible();
});

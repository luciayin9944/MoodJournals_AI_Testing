import { expect, test } from './fixtures.js';


test('user can log in and log out', async ({ page, loginAs }) => {
  await loginAs('login');

  await expect(page.getByText('Login User', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Logout' }).click();

  await expect(page.getByRole('button', { name: 'Login', exact: true })).toBeVisible();
  await expect(page.getByLabel('Email')).toBeVisible();
});

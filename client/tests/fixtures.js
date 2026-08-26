import { expect, test as base } from '@playwright/test';


export const users = {
  login: 'e2e-login@example.com',
  create: 'e2e-create@example.com',
  edit: 'e2e-edit@example.com',
  delete: 'e2e-delete@example.com',
  history: 'e2e-history@example.com',
  ai: 'e2e-ai@example.com',
};

export const test = base.extend({
  loginAs: async ({ page }, provide) => {
    await provide(async (userKey) => {
      await page.goto('/');
      await page.getByLabel('Email').fill(users[userKey]);
      await page.getByLabel('Password').fill('password123');
      await page.getByRole('button', { name: 'Login', exact: true }).click();
      await expect(page).toHaveURL(/\/dashboard$/);
      await expect(page.getByText('Welcome,')).toBeVisible();
    });
  },
});

export { expect };

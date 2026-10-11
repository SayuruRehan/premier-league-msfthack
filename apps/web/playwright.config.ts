import {defineConfig,devices} from '@playwright/test';

export default defineConfig({
  testDir:'./e2e',
  timeout:30_000,
  expect:{timeout:15_000},
  retries:process.env.CI?1:0,
  reporter:process.env.CI?[['list'],['html',{open:'never'}]]:'list',
  use:{
    baseURL:process.env.MATCHSHIFT_TEST_URL||'http://127.0.0.1:4173',
    trace:'retain-on-failure',
    screenshot:'only-on-failure',
  },
  projects:[
    {name:'desktop-chromium',use:{...devices['Desktop Chrome']}},
    {name:'mobile-chromium',use:{...devices['Desktop Chrome'],viewport:{width:390,height:844}}},
  ],
});

import {test,expect} from '@playwright/test';

test('public offline demo loads all assets and never calls a model API',async({page})=>{
  const outgoing:string[]=[];
  page.on('request',request=>{
    if(request.url().includes('/api/')||/openai|foundry|localhost:8000/i.test(request.url())){
      outgoing.push(request.url());
    }
  });
  await page.goto('/',{waitUntil:'networkidle'});
  await expect(page.getByText('The game has a story.')).toBeVisible();
  await expect(page.getByText('PUBLIC OFFLINE DEMO')).toBeVisible();
  await expect(page.getByRole('heading',{name:'Match-changing moments'})).toBeVisible();
  await expect(page.locator('.v4-cue-card').first()).toBeVisible();
  expect(outgoing).toEqual([]);
});

test('every highlight has an on-air cue and a verified multi-agent story',async({page})=>{
  await page.goto('/');
  const cue=page.locator('.v4-cue-card').first();
  await expect(cue).toBeVisible();
  await cue.click();
  await expect(page.locator('.broadcast-lower-third')).toBeVisible();
  await expect(page.locator('.v4-verified')).toBeVisible();
  await expect(page.locator('.v4-trace')).toContainText('TacticalAnalyst');
  await expect(page.locator('.v4-trace')).toContainText('NarrativeDirector');
  await expect(page.locator('.v4-trace')).toContainText('EvidenceVerifier');
  await expect(page.locator('.v4-trace')).toContainText('AudienceAgent');
  await expect(page.locator('.v4-evidence button').first()).toBeVisible();
  await page.locator('.v4-audience button').filter({hasText:'FAN'}).click();
  await expect(page.locator('.v4-verified')).toBeVisible();
  await page.locator('.v4-audience button').filter({hasText:'ANALYST'}).click();
  await expect(page.locator('.v4-verified')).toBeVisible();
  await expect(page.locator('.v4-story')).toContainText('Signal:');
  await page.locator('.v4-audience button').filter({hasText:'BROADCAST'}).click();
  await expect(page.locator('.v4-verified')).toBeVisible();
  await expect(page.locator('.v4-story')).toContainText('WORKFLOW TRACE');
});

test('replay controls and evidence seek are interactive',async({page})=>{
  await page.goto('/');
  await expect(page.locator('.v4-cue-card').first()).toBeVisible();
  await page.locator('.v4-cue-card').first().click();
  const clock=page.locator('#replay-progress');
  const initial=await clock.inputValue();
  expect(Number(initial)).toBeGreaterThan(0);
  await page.locator('.v4-evidence button').first().click();
  expect(Number(await clock.inputValue())).toBeGreaterThan(0);
  await page.getByRole('button',{name:'Play match'}).click();
  await expect(page.getByRole('button',{name:'Pause match'})).toBeVisible();
  await page.getByRole('button',{name:'Pause match'}).click();
  await expect(page.getByRole('button',{name:'Play match'})).toBeVisible();
});

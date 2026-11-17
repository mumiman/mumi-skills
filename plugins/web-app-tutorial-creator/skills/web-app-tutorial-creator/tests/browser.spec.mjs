// OPTIONAL: requires @playwright/test plus an authorized browser environment.
// Test-only fixture; no network/app content is read. Never use this to bypass a denied browser tool.
import {test, expect} from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const app=fs.readFileSync(path.join(root,'examples/app.html'),'utf8');
const css=fs.readFileSync(path.join(root,'assets/overlay.css'),'utf8');
const runtime=path.join(root,'assets/overlay.js');
const spec={title:'Test tour',language:'th',steps:[{id:'open',title:'เปิดแบบฟอร์ม',instruction:'กด New report',target:{selector:'#new-report'},overlay:{}},{id:'title',title:'ชื่อรายงาน',instruction:'กรอกชื่อรายงาน',target:{selector:'#report-title',timeout_ms:500},overlay:{}}]};
async function load(page){await page.setContent(app);await page.addScriptTag({path:runtime});await page.evaluate(({spec,css})=>WATC.configure(spec,{css}).start(),{spec,css});}
test('native dialog, keyboard and repeat initialization',async({page})=>{
 await load(page);await expect(page.locator('[data-watc-root]')).toHaveCount(1);
 await page.locator('#new-report').click();await page.evaluate(()=>WATC.goTo(1));
 await expect.poll(()=>page.evaluate(()=>WATC.getState().state)).toBe('active');
 await page.getByRole('button',{name:'ไปยังจุดที่อธิบาย'}).click();await expect(page.locator('#report-title')).toBeFocused();
 await page.keyboard.press('F6');await expect(page.getByRole('dialog').last()).toBeFocused();
 await page.keyboard.press('Escape');await expect(page.locator('[data-watc-root]')).toHaveCount(0);
 await page.evaluate(()=>{WATC.start();WATC.start();});await expect(page.locator('[data-watc-root]')).toHaveCount(1);
 await page.evaluate(()=>WATC.destroy());await expect(page.locator('[data-watc-root]')).toHaveCount(0);
});
test('mobile tooltip stays in viewport',async({page})=>{
 await page.setViewportSize({width:390,height:844});await load(page);
 const box=await page.locator('[data-watc-root] .tip').boundingBox();
 expect(box.x).toBeGreaterThanOrEqual(0);expect(box.y).toBeGreaterThanOrEqual(0);expect(box.x+box.width).toBeLessThanOrEqual(390);expect(box.y+box.height).toBeLessThanOrEqual(844);
});
test('delayed target and nested scroll recovery',async({page})=>{
 await load(page);await page.evaluate(({css})=>WATC.configure({title:'Dynamic',language:'en',steps:[{id:'late',instruction:'Late',target:{selector:'#late',timeout_ms:30}},{id:'nested',instruction:'Nested',target:{selector:'#nested-target'}}]},{css}).start(),{css});
 await expect.poll(()=>page.evaluate(()=>WATC.getState().state)).toBe('missing');
 await page.evaluate(()=>{const button=document.createElement('button');button.id='late';button.textContent='Late';document.querySelector('#late-container').append(button);});
 await expect.poll(()=>page.evaluate(()=>WATC.getState().state)).toBe('active');
 await page.evaluate(()=>WATC.goTo(1));await expect.poll(()=>page.locator('.scroll').evaluate(el=>el.scrollTop)).toBeGreaterThan(0);
});

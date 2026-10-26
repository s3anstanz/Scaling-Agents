import { chromium } from "playwright";
import { fileURLToPath } from "node:url";

const page_url = new URL("../dist/scaling-agents.html", import.meta.url).href;
const failures = [];
const fail = (msg) => failures.push(msg);
const views = ["home", ...Array.from({ length: 20 }, (_, i) => `lesson-${String(i + 1).padStart(2, "0")}`), "reference"];

const browser = await chromium.launch();
for (const [width, scheme] of [[1280, "light"], [390, "dark"]]) {
  const page = await browser.newPage({ viewport: { width, height: 900 }, colorScheme: scheme });
  await page.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
  page.on("pageerror", (e) => fail(`${width}px: script error: ${e.message}`));
  for (const id of views) {
    await page.goto(`${page_url}#${id}`);
    const state = await page.evaluate((id) => {
      const shown = [...document.querySelectorAll("[data-view]")].filter((v) => !v.hidden).map((v) => v.id);
      return { shown, overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth };
    }, id);
    if (state.shown.length !== 1 || state.shown[0] !== id) fail(`${width}px #${id}: visible views ${JSON.stringify(state.shown)}`);
    if (state.overflow > 1) fail(`${width}px #${id}: page scrolls sideways by ${state.overflow}px`);
  }
  await page.close();
}

const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
await page.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
page.on("pageerror", (e) => fail(`interaction: script error: ${e.message}`));

await page.goto(`${page_url}#lesson-01`);
const l1 = page.locator("#lesson-01");
await l1.locator("[data-component=predict] [data-reveal]").first().click();
if (!(await l1.locator("[data-reveal-panel].is-open").count())) fail("predict: Reveal did not open the answer");
const mcq = l1.locator("[data-component=mcq]").first();
await mcq.locator('.opt[data-correct="true"]').click();
if (!(await mcq.locator(".opt.is-right").count())) fail("mcq: correct option not marked right");
if (!(await mcq.locator('.fb.is-shown[data-verdict="right"]').count())) fail("mcq: right-answer feedback not shown");
await l1.locator(".lab__done input").check();
await page.reload();
if (!(await page.locator("#lesson-01 .lab__done input").isChecked())) fail("lab: 'I ran this lab' did not persist across reload");
if (!(await page.locator('.navitem.is-done[data-target="lesson-01"]').count())) fail("nav: finished lab not ticked in the sidebar");

await page.goto(`${page_url}#lesson-09`);
const stepper = page.locator("#lesson-09 [data-component=stepper]").first();
await stepper.locator('[data-step="1"]').click();
if ((await stepper.locator(".stepper__count").textContent()) !== `Step 2 of ${await stepper.locator(".stepper__frames > li").count()}`) fail("stepper: Next did not advance to step 2");
if (!(await stepper.locator(".is-lit").count())) fail("stepper: no nodes lit on step 2");

await page.goto(`${page_url}#lesson-06`);
const sim = page.locator("#lesson-06 [data-component=scale-sim]");
const before = await sim.locator('[data-o="time"]').textContent();
await sim.locator("input[type=range]").fill("0");
const after = await sim.locator('[data-o="time"]').textContent();
if (before === after) fail("simulator: moving the slider did not change wall-clock");
if ((await sim.locator("output").textContent()) !== "1") fail("simulator: slider at 0 should read 1 agent");

await page.goto(`${page_url}#home`);
const zipText = await page.locator("#starter-zip").textContent();
const zip = Buffer.from(zipText.replace(/\s+/g, ""), "base64");
if (zip.subarray(0, 4).toString("hex") !== "504b0304") fail("starter zip: embedded data is not a zip archive");

const dlButton = page.locator("#dl-btn");
if (await dlButton.isDisabled()) fail("download: button is disabled outside claude.ai");
else {
  try {
    const [download] = await Promise.all([page.waitForEvent("download", { timeout: 5000 }), dlButton.click()]);
    if (download.suggestedFilename() !== "kestrel-starter.zip") fail(`download: saved as ${download.suggestedFilename()}`);
  } catch (e) {
    fail(`download: no file was saved (${e.message.split("\n")[0]})`);
  }
}

const phone = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 3 });
const standalone = await phone.newPage();
standalone.on("pageerror", (e) => fail(`standalone: script error: ${e.message}`));
await standalone.goto(`${new URL("../dist/index.html", import.meta.url).href}#lesson-01`);
const m = await standalone.evaluate(() => ({ mode: document.compatMode, width: window.innerWidth, overflow: document.documentElement.scrollWidth - window.innerWidth }));
if (m.mode !== "CSS1Compat") fail(`standalone: renders in quirks mode (${m.mode})`);
if (m.width !== 390) fail(`standalone on a phone: layout is ${m.width}px wide, not 390`);
if (m.overflow > 1) fail(`standalone on a phone: page scrolls sideways by ${m.overflow}px`);

await browser.close();
if (failures.length) {
  console.error(failures.map((f) => `FAIL ${f}`).join("\n"));
  process.exit(1);
}
console.log(`smoke: ${views.length} views at 2 widths, interactions OK (${fileURLToPath(page_url).split("/").pop()})`);

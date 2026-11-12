import { test } from "@playwright/test";
const OUT = (process.env.CAP_DIR || "cap") + "/";
test("real", async ({ page }) => {
  for (const u of ["", "login", "dashboard", "plans"]) {
    await page.goto("https://quantik.io.vn/" + u, { waitUntil: "networkidle" }).catch(()=>{});
    await page.waitForTimeout(4000);
    await page.screenshot({ path: OUT + "r_" + (u || "home") + ".png", fullPage: true });
  }
});

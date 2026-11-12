import { defineConfig } from "@playwright/test";
export default defineConfig({ testDir: "./tests", testMatch: /zz-video.*\.spec\.ts/, timeout: 240000, reporter: "list",
  use: { actionTimeout: 8000, viewport: { width: 430, height: 932 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, locale: "vi-VN", timezoneId: "Asia/Ho_Chi_Minh",
    // Sandbox cloud có Chromium sẵn tại /opt/pw-browsers; máy thường dùng bản Playwright tự cài.
    launchOptions: require("fs").existsSync("/opt/pw-browsers/chromium") ? { executablePath: "/opt/pw-browsers/chromium" } : {} } });

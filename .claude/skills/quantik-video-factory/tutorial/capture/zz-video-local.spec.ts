import { test, type Page } from "@playwright/test";
import { analysisFixture } from "./fixtures/analysis";
import { quantReportSample } from "./fixtures/quant-report-sample";
const OUT = (process.env.CAP_DIR || "cap") + "/";
const BASE = process.env.LOCAL_BASE || "http://127.0.0.1:3210";
const boxes: Record<string, unknown> = {};
async function snap(page: Page, name: string, targets: Record<string, any> = {}) {
  await page.waitForTimeout(700);
  const b: Record<string, unknown> = {};
  for (const [k, loc] of Object.entries(targets)) b[k] = await loc.boundingBox().catch(() => null);
  boxes[name] = b;
  await page.screenshot({ path: OUT + name + ".png" });
}
const BEST = ["QTA","QTB","QTC","QTD","QTE"], WORST = ["QTV","QTW","QTX","QTY","QTZ"];
function item(symbol: string, i: number, bad: boolean) {
  const s = bad ? 18 - i*2.5 : 86 - i*4.2;
  return { symbol, exchange: i % 2 ? "HNX" : "HOSE", price_vnd: 20000 + i*7300, change_ratio: bad ? -0.012*(i+1) : 0.009*(i+1), change_5d_ratio: bad ? -0.03 : 0.02, change_20d_ratio: bad ? -0.08 : 0.06,
    volume_shares: 900000 - i*90000, average_volume_20_shares: 500000, volume_ratio_20: bad ? 0.7 : 1.8 - i*0.1, price_to_high20_ratio: bad ? 0.82 : 0.97,
    groups: { STRONG: { score: Math.round(s*10)/10, met_count: bad ? 1 : 6 - (i>2?1:0), total_count: 7, unavailable_count: 0 }, ACCUMULATION: { score: bad ? 14.3 : 57.1, met_count: bad ? 1 : 4, total_count: 7, unavailable_count: 0 }, DISTRIBUTION: { score: bad ? 71.4 : 14.3, met_count: bad ? 5 : 1, total_count: 7, unavailable_count: 0 } },
    eligible: true, status: "ELIGIBLE",
    action: bad ? "Đứng ngoài" : "Theo dõi", gate_reasons: bad ? "Dòng tiền âm, phân phối cao" : "Xu hướng & dòng tiền đồng thuận",
    score: Math.round(s), rating: bad ? "Yếu" : (i < 2 ? "Tốt" : "Khá"), holding_sessions: 3 + i, index_trend: "Đi ngang",
    sector: ["Công nghệ","Ngân hàng","Thép","Bán lẻ","Chứng khoán"][i], sector_trend: bad ? "Giảm" : "Tăng", sector_return_20d_pct: bad ? -4.2 + i*0.3 : 3.1 - i*0.4,
    sector_correlation: 0.62 - i*0.05, sector_lead_lag: "Đi cùng ngành", sharpe: bad ? -0.6 - i*0.15 : 1.6 - i*0.18, up_day_ratio_pct: bad ? 41 - i : 56 - i,
    max_drawdown_pct: bad ? -31 - i*2 : -12 - i*1.5, annual_return_pct: bad ? -18 - i*3 : 28 - i*3.5, hmm_regime: bad ? "BEAR" : (i < 3 ? "BULL" : "SIDEWAY"),
    volatility_regime: bad ? "Cao" : "Bình thường", forecast_direction: bad ? "Giảm" : "Tăng", ensemble_return_pct: bad ? -2.4 - i*0.3 : 4.1 - i*0.5,
    roundtrip_cost_pct: 0.6, net_forecast_pct: bad ? -3 - i*0.3 : 3.5 - i*0.5, lock_drawdown_pct: bad ? -7 - i : -4 - i*0.4, probability_loss_gt_3pct: bad ? 38 + i*2 : 8 + i*2,
    liquidity_tier: bad ? "Thấp" : "Cao", adv20_value_vnd: bad ? 4e9 + i*1e9 : 120e9 - i*15e9, capacity_shares: bad ? 3000 : 20000 - i*2000, gap_abs_p95_pct: bad ? 3.9 : 1.6 + i*0.1,
    trade_model_agreement_pct: bad ? 25 : 75 - i*5, commentary: bad ? "Rủi ro phân phối cao; cần quan sát thêm." : "Các mô hình đồng thuận; theo dõi thanh khoản." };
}
function series(n: number, seed: number, end: number) {
  let x = seed; const r = () => { x = (x * 16807) % 2147483647; return x / 2147483647 - 0.5; };
  const raw: number[] = []; let v = 0; for (let k = 0; k < n; k++) { v += r() * 0.035 + 0.0012; raw.push(v); }
  const off = raw[n-1]; return raw.map(q => Math.round(end * Math.exp(q - off) / 100) * 100);
}
async function routes(page: Page) {
  const state = await analysisFixture(page);
  state.report = quantReportSample("complete");
  state.report.symbol = "QTA"; state.report.research!.symbol = "QTA";
  state.report.commentary = { summary: "Tín hiệu đang ở trạng thái theo dõi; các mô hình đồng thuận nhưng điều kiện thời điểm chưa đủ.", detailed: "Hiệu suất lịch sử khá, dòng tiền tích cực, HMM nghiêng về pha tăng. Cần đối chiếu mức sụt giảm, biến động GARCH và rủi ro trong thời gian chờ T+2." };
  const px = series(252, 4242, 102000); const d0 = new Date("2025-10-17");
  const dates = px.map((_, k) => { const t = new Date(d0.getTime() + k * 86400000 * 365 / 252); return t.toISOString().slice(0, 10); });
  Object.assign(state.report.sections.statistics.metrics, { _price_close: px, _price_dates: dates });
  let peak = 0; const dd = px.map((p, k) => { peak = Math.max(peak, p); return { date: dates[k], valuePct: Math.round((p / peak - 1) * 1000) / 10 }; });
  const st = px.map((p, k) => { const m = k < 20 ? p : px[k - 20]; const c = p / m - 1; return { date: dates[k], price: p, state: c > 0.03 ? "BULL" : c < -0.03 ? "BEAR" : "SIDEWAY" }; });
  Object.assign(state.report.research!, { regime: st, drawdown: dd, start: dates[0], end: dates[251] });
  await page.route("**/api/v1/analyses/options**", r => r.fulfill({ contentType: "application/json", body: JSON.stringify({ sessions: ["2026-10-16"], selected_session: "2026-10-16", symbols: ["QTA","FPT","HPG"], ready: true, reason: null }) }));
  await page.route("**/api/v1/screenings/**", async route => {
    const url = new URL(route.request().url()), path = url.pathname.slice(8);
    const json = (d: unknown, s = 200) => route.fulfill({ status: s, contentType: "application/json", body: JSON.stringify(d) });
    if (path === "screenings/latest") return json({ id: "demo-run", target_session: "2026-11-12", published_at: 1794470400, stale: false, refresh_after_seconds: 600 });
    const m = path.match(/^screenings\/(.+)\/results$/);
    if (m) { const bad = url.searchParams.get("group") === "DISTRIBUTION"; return json({ run_id: m[1], group: url.searchParams.get("group"), items: (bad ? WORST : BEST).map((s, i) => item(s, i, bad)) }); }
    const d = path.match(/^screenings\/(.+)\/symbols\/(.+)$/);
    if (d) { const bad = WORST.includes(d[2]); const i = (bad ? WORST : BEST).indexOf(d[2]);
      return json({ run_id: d[1], target_session: "2026-11-12", published_at: 1794470400, input_mode: "COMPLETED_DAILY", observed_at: "2026-11-12T09:00:00+00:00", item: item(d[2], i, bad),
        assessment: bad ? { overall_signal: "Rủi ro", adjusted_signal: "Thận trọng", money_flow: "Tiêu cực", trend: "Giảm", strength: "Yếu", investor_note: "Dòng tiền suy yếu, cần quan sát thêm.", broker_note: "Thanh khoản thấp hơn trung bình 20 phiên." }
                  : { overall_signal: "Theo dõi", adjusted_signal: "Chọn lọc", money_flow: "Tích cực", trend: "Tăng", strength: "Mạnh", investor_note: "Quan sát phản ứng tại vùng hỗ trợ gần nhất.", broker_note: "Thanh khoản cao hơn trung bình 20 phiên." },
        market: { last_close: 1734.75, regime_label: "SIDEWAY", combined_score: 55, risk_label: "Trung bình", change_5d_ratio: 0.01, change_20d_ratio: -0.02, above_ma20: true, atr_pct: 1.4, investor_strategy: "Chọn lọc cơ hội.", broker_strategy: "Theo dõi thị trường." } }); }
    return json({ code: "NOT_FOUND" }, 404);
  });
  return state;
}
test("local", async ({ page }) => {
  const state = await routes(page);
  // SCREENER
  await page.goto(BASE + "/screener"); await page.waitForTimeout(1500);
  const activate = page.getByRole("button", { name: "Kích hoạt kết quả" });
  await snap(page, "s01_banner", { activate });
  await activate.click(); await page.waitForTimeout(1500);
  const best = page.getByRole("region", { name: "5 mã tốt nhất", exact: true });
  const worst = page.getByRole("region", { name: "5 mã nên tránh nhất", exact: true });
  await best.scrollIntoViewIfNeeded(); await page.evaluate(() => window.scrollBy(0, -120));
  await snap(page, "s02_best", { best, qta: best.getByRole("button", { name: "QTA", exact: true }) });
  // horizontal scroll best table
  const scroller = best.getByRole("region");
  await scroller.evaluate(el => { el.scrollLeft = 900; });
  await snap(page, "s03_best_cols", { best });
  await scroller.evaluate(el => { el.scrollLeft = 0; });
  // tooltip on header
  await best.getByRole("button", { name: "Sharpe" }).scrollIntoViewIfNeeded().catch(()=>{});
  await best.getByRole("button", { name: "Sharpe" }).click().catch(()=>{});
  await snap(page, "s04_tooltip", { tip: page.getByRole("tooltip") });
  await page.keyboard.press("Escape"); await page.mouse.click(5, 900);
  await scroller.evaluate(el => { el.scrollLeft = 0; });
  await worst.scrollIntoViewIfNeeded(); await page.evaluate(() => window.scrollBy(0, -120));
  await snap(page, "s05_worst", { worst, qtv: worst.getByRole("button", { name: "QTV", exact: true }) });
  // modal
  await best.scrollIntoViewIfNeeded(); await page.evaluate(() => window.scrollBy(0, -120)); await page.waitForTimeout(400);
  const qta = best.getByRole("button", { name: "QTA", exact: true });
  await snap(page, "s06_tapqta", { qta });
  await qta.click(); await page.waitForTimeout(1200);
  const modal = page.getByRole("dialog");
  await snap(page, "s07_modal", { modal });
  const ql = modal.getByRole("link", { name: /Phân tích Quant/ });
  await ql.scrollIntoViewIfNeeded().catch(()=>{});
  await snap(page, "s08_modal_link", { ql });
  // ANALYSIS
  await ql.click(); await page.waitForURL(/analysis/); await page.waitForTimeout(2000);
  const send = page.getByRole("button", { name: "Gửi yêu cầu Quant QTA", exact: true });
  await send.scrollIntoViewIfNeeded(); await page.evaluate(() => window.scrollTo(0, 0));
  await snap(page, "a01_request", { send });
  await send.click(); await page.waitForTimeout(800);
  const confirm = page.getByRole("button", { name: "Xác nhận", exact: true });
  await snap(page, "a02_confirm", { confirm });
  await confirm.click(); await page.waitForTimeout(1500);
  await snap(page, "a03_queued", { h: page.getByRole("heading", { name: /Đã tiếp nhận/ }) });
  state.status = "SUCCEEDED";
  await page.locator(".quant-report-section").first().waitFor({ timeout: 20000 }); await page.waitForTimeout(1500);
  await page.screenshot({ path: OUT + "a_full.png", fullPage: true });
  const done = page.getByRole("heading", { name: /Đã hoàn tất/ }).first();
  await done.scrollIntoViewIfNeeded(); await page.evaluate(() => window.scrollBy(0, -100));
  await snap(page, "a04_done", { done });
  const nav = page.getByRole("navigation", { name: "Điều hướng module", exact: true });
  await nav.scrollIntoViewIfNeeded(); await page.evaluate(() => window.scrollBy(0, -160));
  await snap(page, "a05_modules", { nav });
  const open = async (label: string, name: string) => {
    await nav.getByRole("button", { name: label, exact: true }).click(); await page.waitForTimeout(900);
    const sec = page.locator(".quant-report-section[open]").first();
    await sec.scrollIntoViewIfNeeded(); await sec.evaluate(el => el.scrollIntoView({ block: "start" })); await page.evaluate(() => window.scrollBy(0, -20));
    await snap(page, name + "_a", { sec });
    await page.evaluate(() => window.scrollBy(0, 700)); await snap(page, name + "_b", {});
    await page.evaluate(() => window.scrollBy(0, 700)); await snap(page, name + "_c", {});
    return sec;
  };
  await open("Hiệu suất", "m01");
  const g = await open("GARCH", "m04");
  await g.getByRole("group", { name: "Góc nhìn biến động GARCH", exact: true }).getByRole("button", { name: "3D", exact: true }).click().catch(()=>{});
  await page.waitForTimeout(800);
  const g3 = g.getByRole("img", { name: /GARCH 3D/ });
  await g3.scrollIntoViewIfNeeded().catch(()=>{}); await page.evaluate(() => window.scrollBy(0, -200));
  await snap(page, "m04_3d", { g3 });
  for (let k = 0; k < 6; k++) { await g3.press("ArrowRight").catch(()=>{}); await page.waitForTimeout(150); await page.screenshot({ path: OUT + `m04_rot${k}.png` }); }
  await open("HMM", "m05");
  await open("Monte Carlo", "m10");
  await open("Đồng thuận", "m09");
  await open("Nhận định", "m16");
  await page.getByText("Biểu đồ bổ sung · Đối chiếu toàn bộ báo cáo", { exact: true }).click(); await page.waitForTimeout(900);
  const fac = page.getByRole("region", { name: "Visual Quant QTA", exact: true });
  await fac.getByRole("group", { name: "Góc nhìn hồ sơ nhân tố", exact: true }).getByRole("button", { name: "3D", exact: true }).click().catch(()=>{});
  await page.waitForTimeout(800);
  const f3 = fac.getByRole("img", { name: "Hồ sơ nhân tố 3D từ báo cáo", exact: true });
  await f3.scrollIntoViewIfNeeded().catch(()=>{}); await page.evaluate(() => window.scrollBy(0, -250));
  await snap(page, "f3d", { f3 });
  const slider = fac.getByRole("slider", { name: "Xoay góc nhân tố", exact: true });
  for (let k = 0; k < 8; k++) { await slider.press("ArrowRight").catch(()=>{}); await slider.press("ArrowRight").catch(()=>{}); await slider.press("ArrowRight").catch(()=>{}); await page.waitForTimeout(150); await page.screenshot({ path: OUT + `f3d_rot${k}.png` }); }
  await fac.getByRole("button", { name: "Radar", exact: true }).click().catch(()=>{}); await page.waitForTimeout(800);
  await snap(page, "fradar", {});
  require("fs").writeFileSync(OUT + "boxes.json", JSON.stringify(boxes, null, 1));
});

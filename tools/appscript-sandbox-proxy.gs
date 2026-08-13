/*  登入版沙箱代理 — 貼進 Apps Script 專案（2026-08-13）
 *
 *  為什麼需要：登入版跑在 HtmlService 沙箱(googleusercontent)，前端對
 *  script.google.com 的 fetch 會「卡住而不 reject」，導致所有寫入互動
 *  （分類切換、進度記錄/刪除、需求單）靜默卡死。index.html 已改成沙箱內
 *  一律走 google.script.run，需要伺服端提供下面三個函式來代打。
 *
 *  貼法：整段貼到 .gs 檔最後面即可（不要動現有的 doGet / doPost）。
 *
 *  ⚠️ 撞名檢查：若你的 .gs 裡已經有 epGet / epPost / getMd 同名函式，
 *     或已有指向同一組網址的常數，請刪掉這裡重複的那一份再貼。
 *     Apps Script 重複宣告 const 會讓整個 script 掛掉。
 */

const DT_EP_URL = 'https://script.google.com/macros/s/AKfycbzmlpV1fpt1RWxVwZj8teUHWw4fs4zpix_3JqCVGX4SeMPIp5Di6_6m_YDRZn4fBQ4/exec';
const DT_GH_BASE = 'https://mac2good909777-commits.github.io/demand-trace/';

/** 代前端 GET 資料端點。kind: 'progress' | 'needs' | 'watch' | 'records' */
function epGet(kind) {
  const url = DT_EP_URL + '?list=' + encodeURIComponent(kind) + '&t=' + Date.now();
  return UrlFetchApp.fetch(url, {
    muteHttpExceptions: true,
    followRedirects: true
  }).getContentText();
}

/** 代前端 POST 寫入端點。body 已是 JSON 字串，原樣轉送。 */
function epPost(body) {
  return UrlFetchApp.fetch(DT_EP_URL, {
    method: 'post',
    contentType: 'text/plain;charset=utf-8',
    payload: body,
    muteHttpExceptions: true,
    followRedirects: true
  }).getContentText();
}

/** 代前端取公司軌跡 md（沙箱內相對路徑會指到 googleusercontent，抓不到）。 */
function getMd(file) {
  const url = DT_GH_BASE + 'companies/' + encodeURIComponent(file) + '?t=' + Date.now();
  return UrlFetchApp.fetch(url, { muteHttpExceptions: true }).getContentText();
}

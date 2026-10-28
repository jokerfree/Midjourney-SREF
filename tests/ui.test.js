// 用 jsdom 验证 index.html 的脚本逻辑（渲染、搜索、分类、弹窗）
// 用法：在 mj-sref-library 目录执行
//   npm i jsdom
//   node tests/ui.test.js
const { JSDOM, VirtualConsole } = require("jsdom");
const path = require("path");

const vc = new VirtualConsole();
const errors = [];
vc.on("jsdomError", e => errors.push("jsdomError: " + e.message));
vc.on("error", (...a) => errors.push("console.error: " + a.join(" ")));

(async () => {
  const dom = await JSDOM.fromFile(path.join(__dirname, "..", "index.html"), {
    runScripts: "dangerously",
    resources: "usable",
    pretendToBeVisual: true,
    virtualConsole: vc,
    beforeParse(window) {
      if (window.HTMLDialogElement) {
        window.HTMLDialogElement.prototype.showModal = function () { this.open = true; };
        window.HTMLDialogElement.prototype.close = function () { this.open = false; };
      }
      window.matchMedia = window.matchMedia || (() => ({ matches: false, addListener() {}, removeListener() {} }));
    },
  });

  const w = dom.window, d = w.document;
  await new Promise(r => w.addEventListener("load", r, { once: true }));
  await new Promise(r => setTimeout(r, 800));

  const out = [];
  const check = (name, cond, extra = "") => out.push(`${cond ? "PASS" : "FAIL"}  ${name}${extra ? "  → " + extra : ""}`);

  check("数据加载", Array.isArray(w.SREF_DATA) && w.SREF_DATA.length > 9000, `${(w.SREF_DATA || []).length} 条`);
  check("目录区渲染", /藏品/.test(d.querySelector("#catalog").textContent));
  check("分类 chips", d.querySelectorAll("#chips .chip").length > 20, `${d.querySelectorAll("#chips .chip").length} 个`);
  check("首屏卡片渲染", d.querySelectorAll("#grid .card").length >= 48, `${d.querySelectorAll("#grid .card").length} 张`);
  check("自动加载到底", d.querySelectorAll("#grid .card").length === (w.SREF_DATA || []).length,
    `${d.querySelectorAll("#grid .card").length} / ${(w.SREF_DATA || []).length}`);
  check("计数文案", /陈列/.test(d.querySelector("#count").textContent), d.querySelector("#count").textContent);

  const q = d.querySelector("#q");
  q.value = "水彩";
  q.dispatchEvent(new w.Event("input", { bubbles: true }));
  await new Promise(r => setTimeout(r, 400));
  const n1 = d.querySelectorAll("#grid .card").length;
  check("中文标签搜索", n1 > 0, `渲染 ${n1} 张，计数 ${d.querySelector("#count").textContent}`);

  q.value = "--sref 1294827730";
  q.dispatchEvent(new w.Event("input", { bubbles: true }));
  await new Promise(r => setTimeout(r, 400));
  check("代码搜索", /陈列 1 件/.test(d.querySelector("#count").textContent), d.querySelector("#count").textContent);

  q.value = "";
  q.dispatchEvent(new w.Event("input", { bubbles: true }));
  await new Promise(r => setTimeout(r, 300));
  const chips = [...d.querySelectorAll("#chips .chip")];
  const target = chips.find(c => /超现实/.test(c.textContent));
  target.click();
  await new Promise(r => setTimeout(r, 200));
  check("分类筛选", /陈列/.test(d.querySelector("#count").textContent) &&
    d.querySelectorAll("#grid .card").length > 0, d.querySelector("#count").textContent);

  d.querySelector("#grid .card").click();
  await new Promise(r => setTimeout(r, 100));
  check("详情弹窗", d.querySelector("#modal").open === true &&
    /--sref \d+/.test(d.querySelector("#mCode").textContent), d.querySelector("#mCode").textContent);

  console.log(out.join("\n"));
  if (errors.length) console.log("\n脚本错误:\n" + errors.slice(0, 5).join("\n"));
  dom.window.close();
  process.exit(errors.length ? 2 : 0);
})();

/* Sandbox Review — vanilla JS, hash routing, no external deps. */
"use strict";

const stage = document.getElementById("stage");
const $ = (sel, el = document) => el.querySelector(sel);

const api = async (path, opts) => {
  const r = await fetch(path, opts);
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return r.json();
};
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

/* --- shared widgets ------------------------------------------------------ */
const vu = (score, passLine = 0.85) => {
  const pct = Math.round(Math.max(0, Math.min(1, score ?? 0)) * 100);
  const good = score >= passLine;
  return `<span class="vu ${good ? "good" : ""}"><i style="width:${pct}%"></i><b style="left:${passLine * 100}%"></b></span>`;
};
const vuRow = (label, score, passLine) => `
  <div class="vu-row"><span class="lbl">${esc(label)}</span>${vu(score, passLine)}
  <span class="val">${score == null ? "—" : score.toFixed(2)}</span></div>`;

const player = (label, src) => `
  <div class="chan"><span class="lbl">${esc(label)}</span>
  <audio controls preload="none" src="${src}"></audio></div>`;

const approveBar = (sid, stage_, iteration) => `
  <div class="row" style="margin-top:10px">
    <button class="approve" data-appr='${JSON.stringify({stage: stage_, verdict: "approved", iteration})}'>Approve</button>
    <button class="reject" data-appr='${JSON.stringify({stage: stage_, verdict: "rejected", iteration})}'>Send back</button>
    <span class="dim mono" data-appr-status></span>
  </div>`;

/* --- views ---------------------------------------------------------------- */
async function viewSessions() {
  const { sessions } = await api("/api/sessions");
  stage.innerHTML = `
    <h1>Sessions</h1>
    <p class="sub">Every sandbox run, newest first. Open one to audition its takes.</p>
    ${sessions.length ? "" : `<div class="panel dim">No sessions yet — start one from the MCP tools (sandbox_start).</div>`}
    ${sessions.map(s => `
      <div class="panel sess" data-open="${esc(s.id)}" role="button" tabindex="0">
        <div><span class="id">${esc(s.id)}</span>
          <div class="dim" style="font-size:12px">${esc(s.genre)} · ${s.bpm} BPM · ${esc(s.key)} · ${s.iterations} take${s.iterations === 1 ? "" : "s"}</div></div>
        ${s.best_score != null ? `<div style="min-width:150px">${vu(s.best_score)}</div>` : "<span></span>"}
        <span class="tag ${s.done_reason === "pass" ? "pass" : s.pending_checkpoint ? "warn" : ""}">
          ${esc(s.pending_checkpoint ? "needs you" : (s.done_reason || s.state.toLowerCase()))}</span>
        <span class="mono dim">${s.best_score != null ? s.best_score.toFixed(2) : ""}</span>
      </div>`).join("")}`;
  stage.querySelectorAll("[data-open]").forEach(el => {
    const go = () => location.hash = `#/session/${el.dataset.open}`;
    el.addEventListener("click", go);
    el.addEventListener("keydown", e => e.key === "Enter" && go());
  });
}

async function viewSession(sid) {
  const st = await api(`/api/sessions/${sid}`);
  const best = st.iterations.reduce((b, it) =>
    (it.scores?.overall ?? -1) > (b?.scores?.overall ?? -1) ? it : b, null);
  const passLine = st.config?.pass_threshold ?? 0.85;
  const cp = st.checkpoints.find(c => c.status === "pending");
  const stamps = stage_ => (st.approvals || []).filter(a => a.stage === stage_)
    .map(a => `<span class="stamp ${a.verdict}">${a.verdict}${a.iteration != null ? " · take " + a.iteration : ""}</span>`).join(" ");

  stage.innerHTML = `
    <h1>${esc(sid)}</h1>
    <p class="sub">${esc(st.genre)} · ${st.bpm} BPM · ${esc(st.key)} · ${esc(st.state)}${st.done_reason ? " (" + esc(st.done_reason) + ")" : ""}</p>

    ${cp ? `<div class="notice"><strong>Needs your call:</strong> ${esc(cp.question)}
      <div class="row" style="margin-top:10px">
        ${cp.options.map(o => `<button data-cp="${esc(cp.id)}" data-decision="${esc(o)}">${esc(o)}</button>`).join("")}
      </div></div>` : ""}

    ${Object.keys(st.plan || {}).length ? `
      <h2>Plan ${stamps("plan")}</h2>
      <div class="panel"><span class="mono">${esc(JSON.stringify(st.plan))}</span>
      ${approveBar(sid, "plan", null)}</div>` : ""}

    <h2>Takes</h2>
    ${st.iterations.length ? "" : `<div class="panel dim">No takes yet.</div>`}
    ${st.iterations.map(it => {
      const roles = Object.keys(it.audio || {}).filter(k => k !== "master");
      return `
      <section class="take ${best && it.index === best.index ? "best" : ""}">
        <div class="take-head"><span class="take-no">TAKE ${String(it.index).padStart(3, "0")}</span>
          <span class="mono dim">overall ${it.scores?.overall?.toFixed(3) ?? "—"} · ${esc(it.report?.verdict ?? "")}</span>
          ${stamps("iteration") ? `<span>${stamps("iteration")}</span>` : ""}</div>
        ${it.audio?.master ? player("master", `/api/sessions/${sid}/audio/${String(it.index).padStart(3, "0")}/master.wav`) : ""}
        ${roles.map(r => player(r, `/api/sessions/${sid}/audio/${String(it.index).padStart(3, "0")}/${r}.wav`)).join("")}
        ${Object.entries(it.scores?.per_role || {}).map(([r, v]) => vuRow(r, v, passLine)).join("")}
        ${it.report?.critique ? `<div class="crit"><strong>${esc(it.report.critique.summary || "")}</strong>
          <ul>${(it.report.critique.priorities || []).map(p => `<li>${esc(p)}</li>`).join("")}</ul></div>` : ""}
        ${approveBar(sid, "iteration", it.index)}
      </section>`;
    }).join("")}

    <h2>Final sign-off ${stamps("final")}</h2>
    <div class="panel">
      <div class="dim" style="font-size:13px">Approving FINAL clears the take for commit to Ableton; rejecting blocks sandbox_commit.</div>
      ${approveBar(sid, "final", best?.index ?? null)}
    </div>`;

  stage.querySelectorAll("[data-cp]").forEach(b => b.addEventListener("click", async () => {
    const notes = prompt("Any direction to pass along? (optional)") || "";
    await api(`/api/sessions/${sid}/checkpoints/${b.dataset.cp}`,
      { method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ decision: b.dataset.decision, notes }) });
    route();
  }));
  wireApprovals(sid);
}

function wireApprovals(sid) {
  stage.querySelectorAll("[data-appr]").forEach(b => b.addEventListener("click", async () => {
    const body = JSON.parse(b.dataset.appr);
    if (body.verdict === "rejected") body.notes = prompt("What should change?") || "";
    await api(`/api/sessions/${sid}/approvals`,
      { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
    const status = b.closest(".row").querySelector("[data-appr-status]");
    if (status) status.textContent = `${body.verdict} ✓`;
  }));
}

async function viewFidelity() {
  const { registry, guide } = await api("/api/fidelity");
  const rows = Object.entries(registry);
  stage.innerHTML = `
    <h1>Fidelity</h1>
    <p class="sub">Measured evidence that a headless render is (or isn't) the Ableton sound.
       Your ears are the judge — play both sides. Calibrate more plugins with
       <span class="mono">python run_harness.py calibrate</span>.</p>
    ${rows.length ? "" : `<div class="panel dim">Nothing calibrated yet.</div>`}
    <div class="panel" style="overflow-x:auto"><table>
      <thead><tr><th>Plugin</th><th>Preset</th><th>Null depth</th><th>Verdict</th><th>Latency</th><th>A / B</th></tr></thead>
      <tbody>${rows.map(([k, e]) => `
        <tr><td>${esc(e.plugin)}</td><td class="mono dim">${esc(e.preset || "—")}</td>
        <td class="null-db">${e.results?.null_depth_db != null ? e.results.null_depth_db + " dB" : "—"}</td>
        <td><span class="tag ${e.label === "measured-identical" ? "pass" : e.label === "diverged" ? "bad" : e.label === "live_only" ? "" : "warn"}">${esc(e.label)}</span></td>
        <td class="mono dim">${e.results?.latency_samples ?? "—"}</td>
        <td style="min-width:280px">${e.audio_pair?.headless ? `
          <div class="ab"><span class="lbl dim mono">HEADLESS</span><audio controls preload="none" src="/api/fidelity/${esc(k)}/audio/headless"></audio></div>
          <div class="ab"><span class="lbl dim mono">ABLETON</span><audio controls preload="none" src="/api/fidelity/${esc(k)}/audio/live"></audio></div>` : "<span class='dim'>—</span>"}</td>
        </tr>`).join("")}</tbody></table></div>
    <h2>Reading the labels</h2>
    <div class="panel">${Object.entries(guide).map(([k, v]) =>
      `<div class="row" style="margin:4px 0"><span class="tag">${esc(k)}</span><span class="dim" style="font-size:13px">${esc(v)}</span></div>`).join("")}</div>`;
}

async function viewEars() {
  const e = await api("/api/ears");
  if (e.error) {
    stage.innerHTML = `<h1>Live Ears</h1>
      <div class="notice err"><strong>${esc(e.error)}</strong><br>${esc(e.fix || "")}</div>`;
    return;
  }
  const s = e.status || {};
  const bars = e.recent_bars || [];
  stage.innerHTML = `
    <h1>Live Ears</h1>
    <p class="sub">What the master bus is doing in Ableton right now (via the Mix Analysis Hub device).</p>
    <div class="panel row spread">
      <span class="tag ${s.playing ? "pass" : ""}">${s.playing ? "playing" : "stopped"}</span>
      <span class="mono">${s.bpm ?? "—"} BPM</span>
      <span class="mono">bar ${s.current_bar ?? "—"}</span>
      <span class="mono dim">${s.cached_bars ?? 0} bars cached</span>
    </div>
    <h2>Recent bars</h2>
    <div class="panel" style="overflow-x:auto"><table>
      <thead><tr><th>Bar</th><th>RMS L/R (dB)</th><th>Correlation</th><th>Width</th></tr></thead>
      <tbody>${bars.slice(-12).reverse().map(b => `
        <tr><td class="mono">${b.bar_number}</td>
        <td class="mono">${b.levels?.rms_l?.toFixed(1)} / ${b.levels?.rms_r?.toFixed(1)}</td>
        <td class="mono">${b.stereo?.correlation?.toFixed(2)}</td>
        <td class="mono">${b.stereo?.width?.toFixed(2)}</td></tr>`).join("")}</tbody>
    </table>${bars.length ? "" : `<p class="dim">No bars yet — press play in Live.</p>`}</div>`;
}

/* --- router + ears LED ---------------------------------------------------- */
async function route() {
  const h = location.hash || "#/sessions";
  document.querySelectorAll(".jack").forEach(a =>
    a.classList.toggle("on", h.startsWith("#/" + a.dataset.view) ||
      (a.dataset.view === "sessions" && h.startsWith("#/session"))));
  try {
    if (h.startsWith("#/session/")) await viewSession(h.split("/")[2]);
    else if (h.startsWith("#/fidelity")) await viewFidelity();
    else if (h.startsWith("#/ears")) await viewEars();
    else await viewSessions();
  } catch (err) {
    stage.innerHTML = `<div class="notice err">Couldn't load this view: ${esc(err.message)}</div>`;
  }
  stage.focus({ preventScroll: true });
}
window.addEventListener("hashchange", route);
route();

async function earsLed() {
  const led = document.getElementById("ears-led");
  try {
    const e = await api("/api/ears");
    led.className = "led " + (e.error ? "stale" : "on");
    led.title = e.error ? e.error : "live ears streaming";
  } catch { led.className = "led"; }
}
earsLed();
setInterval(earsLed, 5000);

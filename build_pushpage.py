#!/usr/bin/env python3
"""Regenerate the GitHub push console page for the price tracker.
Daily flow: update docs/items.json, run build_site.py to re-render docs/index.html, then run this.
Usage: python3 build_pushpage.py <file-to-push-relative-path> [more paths...]
Writes /tmp/pushpage.html and /tmp/pushurl.txt (data: URL). Push = vault fill token into #t, click #go.
"""
import base64, json, sys, urllib.parse

REPO = "price-tracker"
paths = sys.argv[1:] or ["docs/items.json", "docs/index.html"]
files = []
for p in paths:
    with open(p, "rb") as f:
        files.append({"path": p, "b64": base64.b64encode(f.read()).decode(),
                      "msg": "price tracker: update " + p})

html = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>gh push</title></head>
<body style="font-family:monospace;padding:24px">
<h3>price-tracker push</h3>
<input id="t" type="password" placeholder="token" style="width:380px">
<button id="go">push</button>
<pre id="log" style="white-space:pre-wrap;margin-top:16px"></pre>
<script>
const REPO = "%s";
const FILES = %s;
const log = m => { document.getElementById("log").textContent += m + "\\n"; };
async function api(tok, method, url, body) {
  const r = await fetch("https://api.github.com" + url, {
    method,
    headers: {Authorization: "Bearer " + tok, Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"},
    body: body ? JSON.stringify(body) : undefined
  });
  let j = null; try { j = await r.json(); } catch(e) {}
  return {status: r.status, j};
}
document.getElementById("go").addEventListener("click", async () => {
  const tok = document.getElementById("t").value.trim();
  document.getElementById("log").textContent = "";
  try {
    const me = await api(tok, "GET", "/user");
    if (me.status !== 200) { log("AUTH FAIL " + me.status); return; }
    log("authenticated as " + me.j.login);
    for (const f of FILES) {
      const cur = await api(tok, "GET", "/repos/mrwaggles/" + REPO + "/contents/" + f.path);
      const body = {message: f.msg, content: f.b64};
      if (cur.status === 200 && cur.j && cur.j.sha) body.sha = cur.j.sha;
      const put = await api(tok, "PUT", "/repos/mrwaggles/" + REPO + "/contents/" + f.path, body);
      log((put.status === 201 || put.status === 200 ? "ok " : "FAIL " + put.status + " ") + f.path);
    }
    log("DONE");
  } catch (e) { log("ERROR " + e); }
});
</script></body></html>""" % (REPO, json.dumps(files))

with open("/tmp/pushpage.html", "w") as f:
    f.write(html)
with open("/tmp/pushurl.txt", "w") as f:
    f.write("data:text/html;charset=utf-8," + urllib.parse.quote(html))
print("page bytes:", len(html))

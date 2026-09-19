#!/usr/bin/env python3
"""Render docs/index.html statically from docs/items.json. No client JS required."""
import json, html, datetime

def fmt(cur, v):
    return "$%.2f" % v if (cur or "USD") == "USD" else ("%s %.2f" % (cur, v))

def spark(hist, cur):
    pts = [h["price"] for h in hist]
    w, hgt, pad = 340, 64, 6
    mn, mx = min(pts), max(pts)
    span = (mx - mn) or 1
    n = len(pts)
    x = lambda i: (w / 2 if n == 1 else pad + i * (w - 2 * pad) / (n - 1))
    y = lambda v: hgt - pad - (v - mn) * (hgt - 2 * pad) / span
    line = " ".join(("M" if i == 0 else "L") + "%.1f,%.1f" % (x(i), y(p)) for i, p in enumerate(pts))
    dots = "".join('<circle cx="%.1f" cy="%.1f" r="2.6" fill="#0b5fff"/>' % (x(i), y(p)) for i, p in enumerate(pts))
    return ('<svg class="chart" width="%d" height="%d" viewBox="0 0 %d %d" role="img" aria-label="price history">'
            '<path d="%s" fill="none" stroke="#0b5fff" stroke-width="2"/>%s</svg>'
            '<div class="meta">%d check%s &middot; low %s &middot; high %s</div>'
            % (w, hgt, w, hgt, line, dots, n, "" if n == 1 else "s", fmt(cur, mn), fmt(cur, mx)))

def badge(it):
    delta = it["current"] - it["baseline"]
    pct = (delta / it["baseline"] * 100) if it["baseline"] else 0
    if delta < -0.004:
        return '<span class="badge down">&#9660; %s (%.1f%%) vs start</span>' % (fmt(it["currency"], abs(delta)), abs(pct))
    if delta > 0.004:
        return '<span class="badge up">&#9650; %s (%.1f%%) vs start</span>' % (fmt(it["currency"], delta), pct)
    return '<span class="badge flat">at start price</span>'

def card(it):
    rows = "".join("<tr><td>%s</td><td class=\"num\">%s</td><td>%s</td></tr>"
                   % (html.escape(h["date"]), fmt(it["currency"], h["price"]), html.escape(h.get("status", "")))
                   for h in reversed(it["history"]))
    note = (" &middot; " + html.escape(it["baseline_note"])) if it.get("baseline_note") else ""
    status = html.escape(it.get("current_status", ""))
    return """<section class="card">
  <h2>%s</h2>
  <p class="specs">%s &middot; %s</p>
  <div class="row">
    <span class="price">%s</span>
    %s
    <span class="meta">started %s on %s%s</span>
    <a class="buy" href="%s">View product &rarr;</a>
  </div>
  <div class="meta" style="margin-top:4px">%s</div>
  %s
  <table><thead><tr><th>Date</th><th class="num">Price</th><th>Status</th></tr></thead>
  <tbody>%s</tbody></table>
</section>""" % (html.escape(it["name"]), html.escape(it["merchant"]), html.escape(it["specs"]),
                 fmt(it["currency"], it["current"]), badge(it),
                 fmt(it["currency"], it["baseline"]), html.escape(it["baseline_date"]), note,
                 html.escape(it["url"], quote=True), status, spark(it["history"], it["currency"]), rows)

def main():
    data = json.load(open("docs/items.json"))
    items = data["items"]
    cards = "\n".join(card(it) for it in items)
    page = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="color-scheme" content="only light">
<title>Price Tracker</title>
<style>
  :root { color-scheme: only light; --ink:#1c1e21; --muted:#6b7280; --line:#e5e7eb; --good:#0a7d3b; --bad:#b42318; --bg:#fafaf9; }
  html { background:#fafaf9; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; background:#fafaf9; background:var(--bg); color:#1c1e21; color:var(--ink); }
  .wrap { max-width:860px; margin:0 auto; padding:40px 20px 80px; }
  header h1 { font-size:26px; margin:0 0 4px; letter-spacing:-0.01em; }
  header p { margin:0 0 28px; color:#6b7280; color:var(--muted); font-size:14px; }
  .card { background:#ffffff; border:1px solid var(--line); border-radius:14px; padding:22px 24px; margin-bottom:20px; }
  .card h2 { font-size:17px; margin:0 0 2px; }
  .specs { color:#6b7280; color:var(--muted); font-size:13px; margin:0 0 14px; }
  .row { display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
  .price { font-size:30px; font-weight:650; letter-spacing:-0.02em; }
  .meta { font-size:13px; color:#6b7280; color:var(--muted); }
  .badge { display:inline-block; font-size:12px; font-weight:600; padding:3px 10px; border-radius:999px; }
  .badge.down { color:#0a7d3b; background:#e8f6ee; }
  .badge.up { color:#b42318; background:#fdecea; }
  .badge.flat { color:#6b7280; background:#f3f4f6; }
  a.buy { font-size:13px; font-weight:600; color:#0b5fff; text-decoration:none; }
  a.buy:hover { text-decoration:underline; }
  .chart { margin:16px 0 6px; }
  table { width:100%; border-collapse:collapse; font-size:13px; margin-top:10px; }
  th, td { text-align:left; padding:6px 8px; border-bottom:1px solid var(--line); }
  th { color:#6b7280; color:var(--muted); font-weight:600; font-size:12px; text-transform:uppercase; letter-spacing:.04em; }
  td.num, th.num { text-align:right; }
  footer { color:#6b7280; color:var(--muted); font-size:12px; margin-top:28px; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Price Tracker</h1>
    <p>Updated @UPDATED@ &middot; @COUNT@ item@PLURAL@ tracked</p>
  </header>
  <main>
@CARDS@
  </main>
  <footer>Prices checked once daily. View only.</footer>
</div>
</body>
</html>
"""
    page = (page.replace("@UPDATED@", html.escape(data["updated_at"]))
                .replace("@COUNT@", str(len(items)))
                .replace("@PLURAL@", "" if len(items) == 1 else "s")
                .replace("@CARDS@", cards))
    open("docs/index.html", "w").write(page)
    print("rendered", len(items), "items,", len(page), "bytes")

if __name__ == "__main__":
    main()

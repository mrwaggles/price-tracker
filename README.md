# Price Tracker

A small, self-updating price watch. Tracked items live in `docs/items.json`
(name, identifying specs, product URL, baseline price, current price, and
dated price history) and are rendered as a static site from `docs/` via
GitHub Pages.

- Prices are checked once per day; each check appends a history entry.
- An alert email goes out when an item drops below its start-of-tracking
  price or shows a visible sale/coupon.
- On the 1st of each month a digest email lists every tracked item with
  current price and history.
- The site is view-only; items are added or removed through the assistant.

Site: https://mrwaggles.github.io/price-tracker/

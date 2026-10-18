# Price tracker

Daily GitHub Action scrapes prices into `prices.db` (committed back to the repo), judges each price
against its own history (real deal vs gimmick), pushes an alert via ntfy on any change, and publishes a
dashboard to GitHub Pages. Free for a public repo.

## One-time setup

1. Edit `items.json`: one entry per product per shop. `selector` / `was_selector` (CSS) are optional;
   without `selector` the price is read from the page's JSON-LD / meta tags.
2. Push to a **public** GitHub repo (Pages is free only for public repos).
3. Repo > Settings > Pages > Source: **GitHub Actions**.
4. Repo > Settings > Secrets and variables > Actions > new secret `NTFY_TOPIC` = a long random string.
   Install the ntfy app and subscribe to that topic.
5. Actions tab > track > Run workflow. Dashboard URL shows in the run summary.

Edit `events.json` to add sale events (Prime Day, Click Frenzy, EOFY...). Local run:
`pip install -r requirements.txt && python tracker.py scrape && python tracker.py report && python -m http.server -d site`

## Notes

- Judging starts after 14 days of history; the more history, the better the "usual price".
- Some shops block GitHub's datacenter IPs. Those items show up as `FAILED - 403` alerts.
- GitHub pauses scheduled workflows after 60 days without repo activity; the daily data commit counts, but if it ever pauses, re-enable it in the Actions tab.

# Job application worker

Runs on your Mac, outside Docker. Every 30 minutes it asks the backend for your
`PENDING` job entries and opens each supported one in a visible Chrome window.

For each entry it:

1. Sets the entry to `IN_PROGRESS`.
2. Opens the posting and clicks Apply.
3. Fills your email, then **waits for you** to agree to the terms, click NEXT and enter the emailed code.
4. Fills fields whose labels match `profile.json`, uploads your resume, and clicks Next through the steps.
5. **Stops before the final Submit**, takes a screenshot and sets `NEEDS_REVIEW`.
6. Waits while you check the form. If you submit, the entry becomes `SUBMITTED`. If you close the tab, it stays `NEEDS_REVIEW`.

Any error sets `FAILED`, with a screenshot in `screenshots/`.

Supported today: `ORACLE` (Oracle Recruiting Cloud, e.g. JPMorgan Chase). Entries of other
types are skipped and stay `PENDING`.

## Setup

```bash
cd worker
npm install
cp .env.example .env              # backend login, intervals
cp profile.example.json profile.json   # your details and resume path
```

Requires Google Chrome installed, and the Docker stack running (`docker compose up`).

## Run

```bash
npm start      # check now, then every POLL_INTERVAL_MINUTES
npm run once   # check once and exit
```

Keep the terminal visible: it prints `ACTION NEEDED` when you have to do something in Chrome.

## Filling more fields

After each step the worker logs `still empty: …` with the labels of empty fields. Copy any
label you want filled automatically into `profile.json` → `fields`, exactly as written.
It never ticks agreement, consent or certification boxes, and never fills honeypot fields.

## Private files

These are git-ignored and must stay that way:

- `.env`: your backend password
- `profile.json`: your personal details
- `.browser-profile/`: Chrome's saved, logged-in employer sessions
- `screenshots/`: images of filled applications

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

Supported today: `AKAMAI_ORACLECLOUD` (Akamai's careers site, run by
`adapters/akamaiOracleCloud.ts`). Entries of other
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

## Try one URL

Runs the script for a job type against a single posting, without the backend or a job
entry, and without changing any status. Handy for checking a new site. Needs `profile.json`
but not `.env`.

```bash
npm run try -- "<job url>"                    # AKAMAI_ORACLECLOUD by default
npm run try -- "<job url>" AKAMAI_ORACLECLOUD
```

It stops before Submit and keeps Chrome open until you close the window or press Ctrl+C.

## Run now

The **Run now** button on the Job Entries page starts a run without waiting for the next
30-minute check. The worker asks the backend every 10 seconds whether it was clicked, so a
run starts within about 10 seconds. If the worker isn't running, the request waits and runs
when you start it. The page also shows whether the worker is offline, idle or running.
`npm run once` does not listen for Run now.

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

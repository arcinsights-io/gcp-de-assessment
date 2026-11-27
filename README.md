# ARC Insights – GCP data engineering assessment

Thank you for taking this on. You'll build a small but complete data pipeline on Google Cloud, then walk us through it on a 20-minute call. The deadline is in the email we sent you.

There's no trick. We want to see how you structure a pipeline, how you handle messy data, how much Python and SQL you write yourself, and how clearly you explain your choices.

## The scenario

A mobile network operator receives performance counters from its radio cells every 15 minutes. Three equipment vendors send them as files into a landing area. The network team wants one trusted table of daily KPIs per cell, so they can spot cells that are failing or overloaded.

The feeds are not clean. Expect what real feeds do: the same data arriving more than once, corrections sent after the fact, late files, rows that make no sense, and vendors that don't agree on column names or units. [DATA.md](DATA.md) describes the files.

## Before you start

1. **Create your own Google Cloud project.** New accounts get free credit, which is far more than this needs.
2. **Set a budget alert** (Billing → Budgets & alerts) at £10, so nothing surprises you.
3. **Use one region throughout:** `europe-west2` (London) for buckets, BigQuery and services.
4. **Generate the data** (Cloud Shell has Python ready):
   ```bash
   pip install -r requirements.txt
   python data/generate_data.py --out output
   ```
5. **Never commit service-account key files.** The `.gitignore` blocks the common ones; use your own login or the service's identity instead.

Do not create a Cloud Composer environment or leave Dataproc clusters running. They charge by the hour even when idle, and you don't need them here.

## Choose your track

Your email tells you which track we'd like you to take. If it doesn't, take the **Core** track.

### Core track (everyone except the SQL track)

1. **Landing.** Create a Cloud Storage bucket and upload the files from `output/landing/` and `output/reference/`.
2. **Ingestion.** Write a Python service on Cloud Run or Cloud Functions that is triggered when a file lands, reads it (CSV or Parquet) and loads it into a raw BigQuery table. Keep the file name and load time with every row. Loading the same file twice must not double-count anything.
3. **Staging.** Standardise the vendors into one schema (names, types, units). Keep only the latest version of each cell and 15-minute interval. Send rows that fail validation to a quarantine table, with the reason.
4. **Curated.** Build a daily KPI table per cell, joined to the cell reference data, with at least:
   - RRC setup success rate (`rrc_success / rrc_attempts`)
   - drop rate (`erab_drops / rrc_success`)
   - downlink and uplink traffic in GB
   - average availability and peak average active users

   Partition and cluster it sensibly, and note the bytes scanned by a typical query before and after.
5. **Data quality.** At least four checks, for example row counts against files received, duplicates, nulls in keys, freshness. Show their results somewhere a person could read them.
6. **Tests.** pytest tests for your parsing and validation logic.
7. **Write-up.** Fill in [SUBMISSION.md](SUBMISSION.md).

You can build the staging and curated layers in BigQuery SQL, Dataform or dbt. Your choice, but explain it.

### Lead track

Everything in the Core track, plus a low-level design in `docs/LLD.md` (two pages at most) for taking this to production at 10,000 cells and a few hundred files an hour. Cover:

- orchestration choice and why (e.g. Composer, Workflows, event-driven)
- environments, CI/CD and how changes are promoted
- IAM and service accounts
- monitoring, alerting and how a failed or late file is handled at 3am
- backfills and reprocessing
- cost: what drives it and how you'd control it
- how you'd split the work into user stories for a team of three engineers

### SQL and data quality track

1. Upload the files to Cloud Storage and load them into BigQuery raw tables (the `bq` command line or the console is fine).
2. Steps 3, 4 and 5 of the Core track in BigQuery SQL. You can use scheduled queries.
3. A one-page Looker Studio report on your curated table.
4. Fill in [SUBMISSION.md](SUBMISSION.md).

Python is optional on this track, but using it to load files counts in your favour.

## Optional extras

Only once your track is working end to end:

- Terraform for the bucket, datasets and service accounts
- a GitHub Actions workflow that runs your tests on every push
- Dataform or dbt, if you used plain SQL
- a Looker Studio report (Core and Lead tracks)
- a short note on how you'd change the design for streaming, e.g. with Pub/Sub and Dataflow

## Using AI tools

You may use Claude, Copilot, Gemini, ChatGPT or any other assistant. We use them too. Two conditions:

1. Say in SUBMISSION.md what you used and for what.
2. You must be able to explain every part of what you submit. On the call we'll ask you to share your screen and make a small change to your code without an assistant.

## How to submit

- Commit as you go and push to this repository before the deadline. We look at the last commit before the deadline.
- We can't see inside your Google Cloud project, so put screenshots in `docs/screenshots/`: your BigQuery datasets, a sample of the curated table, the quarantine table and your data-quality results.
- Keep the project running until after your call, then delete it.

## The call

20 minutes, booked through the link in your email, recorded with your agreement so we can review it afterwards. Roughly:

- 5 minutes: walk us through your design
- 10 minutes: questions, and one small live change
- 5 minutes: what you'd do next and anything you'd like to ask

Expect to spend 8–12 hours. A working end-to-end pipeline with a clear write-up beats a half-finished one with every extra. If you run out of time, say what's missing and how you would finish it.

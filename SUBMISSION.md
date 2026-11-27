# Submission

Fill this in and keep it short. Bullet points are fine.

**Name:**
**Track:** Core / Lead / SQL and data quality
**Time spent (roughly):**

## What I built

A diagram (an image in `docs/` or a Mermaid block) and a few lines on how data flows from the bucket to the curated table.

## Design choices

For each, what you chose and why:

- Trigger and ingestion service:
- How duplicate files and restated data are handled:
- Validation and quarantine:
- Partitioning and clustering:
- Where transformations live (SQL, Dataform, dbt, Python):

## Data quality results

What your checks found in the data, with numbers.

## Cost

Bytes scanned by a typical query before and after partitioning and clustering, and roughly what this set-up would cost per month if left running.

## AI tools

Which tools you used, and for which parts.

## What's missing, and what I'd do next

Anything you didn't finish, and what you'd change before this went to production.

## How to run it

The commands someone else would need to deploy and run your pipeline.

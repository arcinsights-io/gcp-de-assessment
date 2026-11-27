# Preparing for a GCP data engineering interview

Your interviewer will usually be an architect or a lead data engineer. Expect a conversation about what you've built, plus questions that test whether you understand why things are done a certain way. Some interviews include a short SQL or Python exercise.

## 1. Know your CV line by line

Every bullet is fair game. For each recent role, be ready to answer:

- What was the business problem, and who used what you built?
- What did *you* build, as opposed to the team?
- Which services and tools did you use, and why those?
- What went wrong, and how did you fix it?
- What would you do differently now?

Prepare two or three stories in that shape. Keep each one to about two minutes.

## 2. The GCP data stack

Be able to say what each is for and when you would *not* use it:

| Area | Services |
|---|---|
| Storage and warehouse | Cloud Storage, BigQuery |
| Ingestion and events | Pub/Sub, Eventarc, Storage Transfer, Datastream |
| Processing | Dataflow (Apache Beam), Dataproc and Dataproc Serverless (Spark), Data Fusion |
| Orchestration | Cloud Composer (Airflow), Workflows, Cloud Scheduler |
| Compute for code | Cloud Run, Cloud Functions |
| Transformation | BigQuery SQL, Dataform, dbt |
| Governance | IAM and service accounts, Dataplex, data catalogues such as Collibra |
| Infrastructure | Terraform, Cloud Build, GitHub Actions |

If you've worked mostly on Azure, AWS or Snowflake, map what you know: ADF to Composer or Data Fusion, Databricks to Dataproc, Snowpipe to Pub/Sub plus a load job, Synapse or Snowflake to BigQuery. Interviewers respect a clear mapping more than a bluff.

## 3. Questions worth practising

**SQL**
- A table has several rows per key. How do you keep only the latest? (Window functions, `QUALIFY`.)
- Compute a rate per day per cell, then the cells in the worst 5%.

**BigQuery**
- A daily query on a very large table has become expensive. What do you check?
- How do partitioning and clustering differ, and how do you choose the columns?

**Pipelines**
- A file lands in a bucket. How does it get into BigQuery? What happens if it arrives twice?
- A task fails at 3am. How does your pipeline recover, and how do you find out?
- Why would you choose Parquet over CSV?
- When would you use Cloud Run rather than a Cloud Function? Dataflow rather than BigQuery SQL?

**Engineering practice**
- How does your code get from your laptop to production?
- What do you test in a data pipeline, and how?
- Your branch has a conflict with main. What do you do?
- How does a service get permission to read a bucket? (Service accounts, least privilege, no key files.)

**How you work**
- Tell us about a task you were given with very little detail.
- What did you last document, and who used it?
- What in this job description have you not done yet?

## 4. On the day

- Test your camera, microphone and screen sharing beforehand.
- Have your CV and your assessment repository open.
- If you don't know something, say so, then explain how you would find out or approach it. That counts in your favour.
- Ask the interviewer a question or two about the team, the data and how they deliver.

## 5. When ARC Insights represents you

- Leave rates, start dates and contract terms to ARC. If asked, say ARC is handling them.
- Don't contact the client or their end customer directly about this role.
- Tell us straight after the interview how it went and what you were asked.

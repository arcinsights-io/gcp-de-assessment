# The data

`python data/generate_data.py --out output` writes three days of data for 60 cells.

## Reference data

`output/reference/cells.csv`, one row per known cell:

| Column | Meaning |
|---|---|
| cell_id | Cell identifier, e.g. `C00001` |
| site_id | The mast the cell is on. One site can carry several cells. |
| vendor | `vendor_a`, `vendor_b` or `vendor_c` |
| region | Region of the network |
| technology | `4G` or `5G` |
| latitude, longitude | Location of the site |

## Counter files

`output/landing/<arrival date>/<vendor>_<batch start>.<csv|parquet>`

Each file holds six hours of 15-minute intervals for one vendor's cells. The folder date is the day the file arrived, which is not always the day the data is for.

### Vendors A and C (CSV)

| Column | Meaning |
|---|---|
| period_start | Start of the 15-minute interval, UTC, ISO 8601 |
| cell_id | Cell identifier |
| rrc_attempts | Connection set-up attempts |
| rrc_success | Successful connection set-ups |
| erab_drops | Connections dropped abnormally |
| dl_volume_mb | Downlink traffic in megabytes |
| ul_volume_mb | Uplink traffic in megabytes |
| avg_active_users | Average active users in the interval |
| availability_pct | Percentage of the interval the cell was available |
| generated_at | When the vendor's system exported the file, UTC |

### Vendor B (Parquet)

Same measures, different names and units:

| Column | Maps to | Note |
|---|---|---|
| interval_start_utc | period_start | |
| cell | cell_id | |
| rrc_conn_attempts | rrc_attempts | |
| rrc_conn_success | rrc_success | |
| erab_abnormal_releases | erab_drops | |
| dl_volume_kb | dl_volume_mb | **kilobytes** |
| ul_volume_kb | ul_volume_mb | **kilobytes** |
| avg_active_users | avg_active_users | |
| cell_availability | availability_pct | |
| export_ts | generated_at | |

## Rules the business has given you

- A cell and 15-minute interval should appear once in the curated data. If a vendor sends the same interval again, the most recent export wins.
- Rows that break basic logic (for example, more successes than attempts) must not reach the curated layer, but must not be silently lost either.
- Cells that are not in the reference data still need reporting to the network team.

"""Generate the synthetic cell-performance feeds for the ARC Insights GCP data engineering assessment.

Run it once (Cloud Shell works fine):

    pip install -r requirements.txt
    python data/generate_data.py --out output

It writes:
    output/reference/cells.csv                       reference data for every known cell
    output/landing/<YYYY-MM-DD>/<vendor>_<...>.csv   15-minute counters from vendors A and C
    output/landing/<YYYY-MM-DD>/<vendor>_<...>.parquet  15-minute counters from vendor B

The feeds behave like real ones. Not every file or row is clean, and the same data
can arrive more than once. Finding and handling that is part of the task.
The output is the same every time for a given --seed.
"""
import argparse
import csv
import datetime as dt
import os
import random

import pyarrow as pa
import pyarrow.parquet as pq

VENDORS = {"vendor_a": "csv", "vendor_b": "parquet", "vendor_c": "csv"}
REGIONS = ["North", "Midlands", "London", "South West", "Scotland"]
BATCH_HOURS = 6          # each file holds 6 hours of 15-minute intervals
INTERVAL_MIN = 15


def make_cells(rng, n_cells):
    cells = []
    for i in range(1, n_cells + 1):
        vendor = list(VENDORS)[(i - 1) % len(VENDORS)]
        cells.append({
            "cell_id": f"C{i:05d}",
            "site_id": f"S{(i + 1) // 2:04d}",
            "vendor": vendor,
            "region": REGIONS[i % len(REGIONS)],
            "technology": "5G" if i % 4 == 0 else "4G",
            "latitude": round(50.0 + rng.random() * 8.5, 5),
            "longitude": round(-5.5 + rng.random() * 7.2, 5),
        })
    return cells


def counters(rng, cell, period_start):
    hour = period_start.hour
    load = 0.25 + 0.75 * max(0.0, 1 - abs(hour - 18) / 12)    # busier in the evening
    if cell["technology"] == "5G":
        load *= 1.6
    attempts = int(rng.randint(400, 900) * load) + 20
    success = attempts - rng.randint(0, max(1, attempts // 40))
    dl_mb = round(rng.uniform(800, 2500) * load, 3)
    return {
        "rrc_attempts": attempts,
        "rrc_success": success,
        "erab_drops": rng.randint(0, max(1, attempts // 150)),
        "dl_volume_mb": dl_mb,
        "ul_volume_mb": round(dl_mb * rng.uniform(0.08, 0.2), 3),
        "avg_active_users": round(rng.uniform(5, 60) * load, 2),
        "availability_pct": 100.0 if rng.random() > 0.03 else round(rng.uniform(70, 99.9), 2),
    }


def iso(ts):
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def build_rows(rng, cells, batch_start, generated_at):
    rows = []
    for step in range(BATCH_HOURS * 60 // INTERVAL_MIN):
        period = batch_start + dt.timedelta(minutes=INTERVAL_MIN * step)
        for cell in cells:
            row = {"period_start": iso(period), "cell_id": cell["cell_id"]}
            row.update(counters(rng, cell, period))
            row["generated_at"] = iso(generated_at)
            rows.append(row)
    return rows


def to_vendor_b(rows):
    """Vendor B sends Parquet, names columns differently and reports volumes in KB."""
    out = []
    for r in rows:
        out.append({
            "interval_start_utc": r["period_start"],
            "cell": r["cell_id"],
            "rrc_conn_attempts": r["rrc_attempts"],
            "rrc_conn_success": r["rrc_success"],
            "erab_abnormal_releases": r["erab_drops"],
            "dl_volume_kb": None if r["dl_volume_mb"] is None else round(r["dl_volume_mb"] * 1024, 1),
            "ul_volume_kb": None if r["ul_volume_mb"] is None else round(r["ul_volume_mb"] * 1024, 1),
            "avg_active_users": r["avg_active_users"],
            "cell_availability": r["availability_pct"],
            "export_ts": r["generated_at"],
        })
    return out


def write_file(path, fmt, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if fmt == "csv":
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    else:
        pq.write_table(pa.Table.from_pylist(rows), path)


def plant_bad_rows(rng, rows, n):
    """A few rows that should never reach the curated layer."""
    kinds = ["null_cell", "success_gt_attempts", "negative_volume", "bad_timestamp", "unknown_cell"]
    for _ in range(n):
        r = rows[rng.randrange(len(rows))]
        kind = rng.choice(kinds)
        if kind == "null_cell":
            r["cell_id"] = None
        elif kind == "success_gt_attempts":
            r["rrc_success"] = r["rrc_attempts"] + rng.randint(5, 50)
        elif kind == "negative_volume":
            r["dl_volume_mb"] = -abs(r["dl_volume_mb"])
        elif kind == "bad_timestamp":
            r["period_start"] = r["period_start"].replace("T", " ").replace("Z", "") + " BST"
        elif kind == "unknown_cell":
            r["cell_id"] = "C99999"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default="output")
    p.add_argument("--days", type=int, default=3)
    p.add_argument("--cells", type=int, default=60)
    p.add_argument("--start", default="2026-11-02", help="first day, YYYY-MM-DD")
    p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()

    rng = random.Random(a.seed)
    cells = make_cells(rng, a.cells)
    os.makedirs(os.path.join(a.out, "reference"), exist_ok=True)
    with open(os.path.join(a.out, "reference", "cells.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(cells[0]))
        w.writeheader()
        w.writerows(cells)

    start = dt.datetime.strptime(a.start, "%Y-%m-%d")
    written = []
    held_back = []          # files that will arrive late
    for d in range(a.days):
        day = start + dt.timedelta(days=d)
        for vendor, fmt in VENDORS.items():
            vcells = [c for c in cells if c["vendor"] == vendor]
            for b in range(24 // BATCH_HOURS):
                batch_start = day + dt.timedelta(hours=b * BATCH_HOURS)
                generated = batch_start + dt.timedelta(hours=BATCH_HOURS, minutes=rng.randint(5, 40))
                rows = build_rows(rng, vcells, batch_start, generated)
                if rng.random() < 0.5:
                    plant_bad_rows(rng, rows, rng.randint(1, 4))
                data = to_vendor_b(rows) if vendor == "vendor_b" else rows
                name = f"{vendor}_{batch_start:%Y%m%d_%H%M}.{fmt}"
                arrival_day = day
                # one batch on day 1 arrives two days late
                if d == 0 and vendor == "vendor_c" and b == 1 and a.days >= 3:
                    arrival_day = day + dt.timedelta(days=2)
                    held_back.append(name)
                path = os.path.join(a.out, "landing", f"{arrival_day:%Y-%m-%d}", name)
                write_file(path, fmt, data)
                written.append((path, fmt, rows, vendor, batch_start))

    # the same file delivered twice under a different name
    path, fmt, rows, vendor, batch_start = written[len(written) // 3]
    dup = path.replace(f".{fmt}", f"_resend.{fmt}")
    write_file(dup, fmt, to_vendor_b(rows) if vendor == "vendor_b" else rows)

    # a restatement: later export of part of an earlier batch with corrected counters
    path, fmt, rows, vendor, batch_start = written[len(written) // 2]
    later = dt.datetime.strptime(rows[0]["generated_at"], "%Y-%m-%dT%H:%M:%SZ") + dt.timedelta(hours=9)
    restated = []
    for r in rows[: len(rows) // 4]:
        if r["cell_id"] is None:
            continue
        r2 = dict(r)
        r2["rrc_attempts"] = (r2["rrc_attempts"] or 0) + 37
        r2["rrc_success"] = (r2["rrc_success"] or 0) + 30
        r2["generated_at"] = iso(later)
        restated.append(r2)
    rdir = os.path.dirname(path)
    rname = f"{vendor}_{batch_start:%Y%m%d_%H%M}_restated.{fmt}"
    write_file(os.path.join(rdir, rname), fmt, to_vendor_b(restated) if vendor == "vendor_b" else restated)

    n_files = sum(len(fs) for _, _, fs in os.walk(os.path.join(a.out, "landing")))
    print(f"Wrote {len(cells)} cells and {n_files} feed files under {a.out}/")


if __name__ == "__main__":
    main()

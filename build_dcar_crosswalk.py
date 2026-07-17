"""Build an auditable NCBI GeneID-to-DCAR locus-tag crosswalk for carrot."""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

PROJECT = Path(r"I:\transcriptomica\daucus_carota")
NCBI_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
DCAR = re.compile(r"\bDCAR_\d+\b", re.IGNORECASE)


def read_genes(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["GeneID"]: row.get("Gene", "") for row in csv.DictReader(handle, delimiter="\t") if row.get("GeneID")}


def fetch(gene_ids: list[str]) -> dict[str, object]:
    query = urlencode({"db": "gene", "id": ",".join(gene_ids), "retmode": "json", "tool": "carrot_consultant"})
    request = Request(NCBI_URL, data=query.encode("utf-8"), headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urlopen(request, timeout=60) as response:
        return json.load(response).get("result", {})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotation", type=Path, default=PROJECT / "07_annotation" / "Annotation_master.tsv")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "reference" / "DCAR_crosswalk.tsv")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--start-batch", type=int, default=0, help="Zero-based batch offset for resumable downloads.")
    parser.add_argument("--max-batches", type=int, default=0, help="Number of batches to fetch; 0 fetches the remainder.")
    args = parser.parse_args()
    genes = read_genes(args.annotation)
    ids = sorted(genes)
    batches = [ids[start:start + args.batch_size] for start in range(0, len(ids), args.batch_size)]
    selected = batches[args.start_batch:args.start_batch + args.max_batches if args.max_batches else None]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if args.start_batch == 0 else "a"
    with args.output.open(mode, encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["GeneID", "LOC", "DCAR", "Source"], delimiter="\t")
        if args.start_batch == 0: writer.writeheader()
        for offset, batch in enumerate(selected, start=args.start_batch):
            summaries = fetch(batch)
            for gene_id in batch:
                summary = summaries.get(gene_id, {})
                match = DCAR.search(str(summary.get("otheraliases", ""))) if isinstance(summary, dict) else None
                if match:
                    writer.writerow({"GeneID": gene_id, "LOC": genes[gene_id], "DCAR": match.group(0).upper(), "Source": "NCBI Gene ESummary"})
            handle.flush()
            print(f"NCBI batch {offset + 1}/{len(batches)}", flush=True)
            if offset + 1 < len(batches): time.sleep(0.35)
    print(f"Wrote batches {args.start_batch + 1}–{args.start_batch + len(selected)} to {args.output}")


if __name__ == "__main__":
    main()

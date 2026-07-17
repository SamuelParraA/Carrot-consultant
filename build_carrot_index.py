#!/usr/bin/env python3
"""Build the standalone carrot-expression SQLite index from Peipers outputs."""

from __future__ import annotations

import csv
import sqlite3
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parent
PROJECT = Path(r"I:\transcriptomica\daucus_carota")


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        yield from csv.DictReader(handle, delimiter="\t")


def main() -> None:
    annotation = {row["GeneID"]: row for row in read_tsv(PROJECT / "07_annotation" / "Annotation_master.tsv")}
    aliases: dict[str, set[str]] = defaultdict(set)
    for row in read_tsv(PROJECT / "08_knowledge" / "Aliases.tsv"):
        if row["Alias"].strip(): aliases[row["GeneID"]].add(row["Alias"].strip())
    knowledge: dict[str, set[str]] = defaultdict(set)
    for row in read_tsv(PROJECT / "09_reports" / "knowledge" / "carotenoids" / "Knowledge_panel.tsv"):
        knowledge[row["GeneID"]].add(row["CanonicalName"])
    metadata = list(read_tsv(PROJECT / "00_metadata" / "sample_metadata.tsv")); samples = [row["SampleID"] for row in metadata]
    database = ROOT / "rnaseq_index.sqlite"; database.unlink(missing_ok=True)
    con = sqlite3.connect(database)
    con.executescript("""
        CREATE TABLE experiments (experiment_id TEXT PRIMARY KEY, name TEXT, path TEXT, metadata_path TEXT);
        CREATE TABLE genes (gene_id TEXT PRIMARY KEY, alias TEXT, name TEXT, description TEXT, go TEXT, interpro TEXT, pfam TEXT, dbxref TEXT, seqid TEXT, start INTEGER, end INTEGER, strand TEXT, exon_count INTEGER, gene_length INTEGER, mrna_length INTEGER, transcripts TEXT, search_text TEXT);
        CREATE TABLE gene_annotations (gene_id TEXT, source TEXT, field TEXT, value TEXT);
        CREATE TABLE samples (experiment_id TEXT, sample TEXT, label TEXT, timepoint TEXT, replicate TEXT, group_name TEXT, treatment TEXT, color TEXT, comments TEXT, sort_order INTEGER, PRIMARY KEY (experiment_id, sample));
        CREATE TABLE expression (experiment_id TEXT, gene_id TEXT, sample TEXT, tpm REAL, reads REAL, PRIMARY KEY (experiment_id, gene_id, sample));
        CREATE INDEX idx_gene_search ON genes(search_text); CREATE INDEX idx_expr_gene ON expression(experiment_id, gene_id);
    """)
    experiment = "carrot_root_development"
    con.execute("INSERT INTO experiments VALUES (?,?,?,?)", (experiment, "Raíz de zanahoria: luz y desarrollo", "standalone", "sample_metadata.csv"))
    colors = {"Dark_4w": "#4c566a", "Dark_8w": "#2e3440", "Light_8w": "#e6a93d"}
    condition_names = {"Dark_4w": "Raíz en oscuridad · 4 semanas", "Dark_8w": "Raíz en oscuridad · 8 semanas", "Light_8w": "Raíz expuesta a luz · 8 semanas"}
    con.executemany("INSERT INTO samples VALUES (?,?,?,?,?,?,?,?,?,?)", [
        (experiment, row["SampleID"], condition_names.get(row["Group"], row["Group"]), condition_names.get(row["Group"], row["Group"]), row["Replicate"], row["Group"], "Raíz expuesta a luz" if row["Light"].casefold() == "light" else "Raíz desarrollada en oscuridad", colors.get(row["Group"], ""), f"{row['Tissue']}; {row['Light']}", index)
        for index, row in enumerate(metadata, 1)
    ])
    expression_rows = []
    for row in read_tsv(PROJECT / "06_expression" / "Gene_TPM.tsv"):
        gene_id = row["GeneID"]; info = annotation.get(gene_id, {})
        alias = "; ".join(sorted(aliases.get(gene_id, set()) | knowledge.get(gene_id, set())))
        description = unquote(info.get("Product") or row.get("Product", ""))
        search = " ".join([gene_id, row.get("Gene", ""), alias, description, info.get("Biotype", "")]).lower()
        con.execute("INSERT INTO genes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (gene_id, alias, row.get("Gene", gene_id), description, info.get("Biotype", ""), "", "", gene_id, info.get("Chromosome", ""), int(info.get("Start") or 0), int(info.get("End") or 0), info.get("Strand", ""), int(row.get("TranscriptCount") or 0), max(0, int(info.get("End") or 0) - int(info.get("Start") or 0) + 1), 0, "", search))
        for canonical in sorted(knowledge.get(gene_id, set())): con.execute("INSERT INTO gene_annotations VALUES (?,?,?,?)", (gene_id, "Knowledge Engine", "CanonicalName", canonical))
        expression_rows.extend((experiment, gene_id, sample, float(row.get(sample) or 0), 0.0) for sample in samples)
    con.executemany("INSERT INTO expression VALUES (?,?,?,?,?)", expression_rows); con.commit(); con.close()
    print(f"Standalone index created: {database} ({len(annotation):,} genes; {len(samples)} samples)")


if __name__ == "__main__": main()

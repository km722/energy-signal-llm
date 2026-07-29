# Labeled data

Two hand-labeled gold sets, used to measure the LLM extraction stage (see LABELLING_GUIDE.md
at the repo root for the labelling rules).

- `gold.csv` - 100 headlines sampled at random from the energy pull (random_state=42).
  Hand-labelled. Estimates pipeline accuracy on the real headline stream.
- `gold_enriched.csv` - 40 headlines sampled from the weather pull. Hand-labelled.
  Deliberately event-heavy so per-class accuracy is measurable (the random sample
  contains only 2 events).
- `gold_labeled.csv` / `gold_enriched_labeled.csv` - the raw Excel exports the two files
  above were validated from. Kept as the record of the original hand labelling; dates in
  these were reformatted by Excel, so downstream code never reads them directly.

The unlabeled sampling scaffolds are not stored; notebooks/build_gold_set.ipynb
regenerates them deterministically.

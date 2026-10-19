# Frozen synthetic evaluation set v1

20 invented items, including near duplicates and two claimed records. 12 positive and 6 negative query cases are stored separately. Each label includes rationale. The related-category positive treats an explicitly requested related suggestion as relevant, not as an exact match or ownership proof; inspect this case separately in reports.

Created after the vocabulary and weights were fixed in the foundation. Frozen before the first evaluation run for B05. No aliases, weights, threshold or broadening rules are tuned to these results. This small, authored set is not an independent campus study or proof of generalization. Known limitations deliberately remain represented, including an unsupported color.

The ranker never reads queries.json or relevant_ids. The evaluation runner sends only query and broaden to the actual search endpoint. It seeds a temporary database and generates harmless sample JPEGs; no demo database or real uploads are used.

Any future algorithm tuning needs a separate development set. Do not edit this v1 set to hide failures. Record a new dataset version and explain changes if future testing needs more coverage.

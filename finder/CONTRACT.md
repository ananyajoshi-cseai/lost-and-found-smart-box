# Finder function contract v1

This is a local Python contract, not an HTTP API. Canonical item keys: id (unique positive integer), category/color/location (supported strings), brand/mark (supported strings or null), status (available or returned). Only synthetic public facts are stored; no private details, photographs or contact fields.

parse(text) returns {positive:{field:value}, excluded:{field:[values]}, ambiguous:[fields]}. It lowercases ASCII tokens, matches longest phrases first and recognizes immediate not/no/without. Unknown words are ignored; complex negation and typos require user correction. Multiple positive values or positive/negative conflict for a field request clarification.

rank(parsed, items, broaden=False) returns up to three {id,score,reasons,strong_candidate,related,coverage,coverage_text,denominator} records. reasons maps each supplied positive field to earned points, as proposed. Coverage and denominator are explicit additions needed for honest interpretation. Weight category=40, color=25, brand=15, location=10, mark=10. Threshold is 50 before rounding, scores round to two decimals; ordering is returned score descending then ID ascending. The score is agreement over supplied positive fields, not ownership confidence.

Any non-available item or excluded-value match is ineligible. Ambiguous/no-positive queries produce no ranked results. With a supplied category, exact eligible items take precedence; only an empty exact pool plus broaden=True enables BFS. Related items earn zero category points. Strong candidate means supplied category/color/brand agree. It never authorizes a return.

bfs(category, limit=2) returns category-to-distance mappings. Edges are bidirectional for search but logical IsA relationships remain parent-directed. Bottle -> personalitems -> campusitem/umbrella/keys is the worked trace.

load_items(path=None) returns validated records, initializing from the seed only when missing. add_item(values,path=None) accepts all five public fields, allocates an ID under the file lock and saves available. mark_returned(id,path=None) requires an existing available record, persists returned and rejects repeated/unknown IDs. Invalid or corrupt files raise errors; the UI shows failure rather than success. The default runtime file is ignored by Git; optional FINDER_DATA_PATH isolates demos/tests. Mutation locks have a five-second timeout. No hosted concurrency or authenticated staff service is claimed.

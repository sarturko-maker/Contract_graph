# Build report, DCG v0.1.0

This file is the review interface. It records what the build produced, what it checked, every
judgement call made while generating the package, and everything I believe is missing from
`build/data.py`. Read it line by line; that is what it is for.

Generated package: 16 files from one source module. Command: `python3 build/build.py` from the
repository root. Python 3.11, standard library only (`csv`, `html`, `io`, `re`, `sys`, `textwrap`,
`pathlib`). No third-party imports, no network access, no installs.

## Fresh-run test

Generated outputs (`families/`, `registries/`, `sample/`, `explainer.html`) were deleted and the
build was run from scratch. It exited 0. It was then run a second time and every generated file was
byte-identical to the first run, confirmed by md5sum across all 16 files. The printed log was
identical too, apart from the absolute repository path.

```
$ rm -rf families registries sample explainer.html
$ python3 build/build.py
```

## Validation output, in full

The following is the complete, unedited console output of the fresh run.

```text
Distributor Contract Graph v0.1.0, build
Repository root: /home/user/Contract_graph

Files written
     families/customers.md                21567 bytes
     families/suppliers.md                15199 bytes
     families/vendors.md                  12748 bytes
     families/overlays.md                  3382 bytes
     families/README.md                   11235 bytes
     registries/node_types.csv             3446 bytes
     registries/edge_types.csv             7638 bytes
     registries/families.csv              25716 bytes
     registries/aliases.csv               14647 bytes
     registries/properties.csv             2937 bytes
     registries/overlays.csv               2924 bytes
     registries/standards_map.csv          4196 bytes
     sample/nodes.csv                      5676 bytes
     sample/edges.csv                      3424 bytes
     sample/README.md                     11228 bytes
     explainer.html                      122770 bytes

Sample node columns: id:ID, name, :LABEL, layer, appointment, captured_at, category, claim_date, commercial_completeness, country, currency, effective_from, eid, family, flow_down, function, governing_law, is_ours, jurisdiction, modality, mpn, order_date, paper, payment_terms, recorded_at, role, sali_tag, scheme, scope, status, time_limited, type, valid_from, valid_to, value, version
Sample edge columns: :START_ID, :END_ID, :TYPE, captured_at, effective_from, function, role, their_part_no, valid_from, version

Validation
========================================================================
1. Sample edge endpoints resolve            PASS (83 edges, 166 endpoints checked)
2. Node labels map to the node registry     PASS (22 distinct labels)
3. Edge types match the edge registry       PASS (33 distinct types)
4. Family codes unique, alias hints resolve PASS (39 codes, 367 aliases, 24 family-neutral)
5. Survival invariant on the sample         PASS (5 direct, 0 inherited, 1 exempt, 0 failing; 4/4 orders have ordered_by)

   Party edges, node by node
     direct      DOC-MSA-2021   Master
     direct      DOC-LPA-DE     Participation
     direct      DOC-LPA-NL     Participation
     direct      DOC-DIST-2018  Master
     direct      DOC-OF2        WorkInstrument
     exempt      DOC-OF1        WorkInstrument
   DOC-SMSA is shared terms on the vendor's paper, so it is exempt as a shared_terms node; the signed order form carries the party edges, which is the point the sample makes.

6. Counts
     families         36  expected   36  ok
     overlays          6  expected    6  ok
     node_types       29  expected   29  ok
     edge_types       60  expected   60  ok
     aliases         367  expected  367  ok
     properties       28  expected   28  ok
     standards        19  expected   19  ok
     sample_nodes     62  expected   62  ok
     sample_edges     83  expected   83  ok
     families.csv     39  (36 families plus the C0, S0 and V0 catch-all rows)

7. explainer.html details blocks            PASS (42, expected 42)
8. No em dashes anywhere in the repository  PASS (20 files scanned)

Warnings (1)
     invariant exemption: DOC-OF1 (WorkInstrument). Superseded 2023 order form. data.py gives party edges to the current order form (DOC-OF2) only, and DOC-OF1's governed-by parent DOC-SMSA is exempt shared terms. Logged in BUILD-REPORT.md as a data gap, not fixed by inventing an edge.

Validation passed. 16 files written, 1 warning(s).
```

## Counts asserted

Every count below is asserted in `build/build.py`; a mismatch fails the build.

| Thing | Count | Expected | Source |
| --- | --- | --- | --- |
| Contract families | 36 | 36 | `data.FAMILIES` (13 customer, 12 supplier, 11 vendor) |
| Overlays | 6 | 6 | `data.OVERLAYS` |
| Node types | 29 | 29 | `data.NODE_TYPES` |
| Edge types | 60 | 60 | `data.EDGE_TYPES` |
| Aliases | 367 | 367 | `data.ALIASES` |
| Properties | 28 | 28 | `data.PROPERTIES` |
| Standards | 19 | 19 | `data.STANDARDS` |
| Sample nodes | 62 | 62 | `data.SAMPLE_NODES` |
| Sample edges | 83 | 83 | `data.SAMPLE_EDGES` |
| `families.csv` rows | 39 | n/a | 36 families plus the C0, S0 and V0 catch-all rows |
| `explainer.html` details blocks | 42 | 42 | 36 families plus 6 overlays |

## Independent checks run outside the build

These were run as a separate verification pass and are not part of `build/build.py`, which stays
standard library only.

| Check | Result |
| --- | --- |
| Every CSV parsed with `csv.reader` | 9 files, no ragged rows, no CRLF, valid UTF-8 |
| Every CSV parsed with pandas 3.0.5 | Row counts and headers match the `csv` module exactly |
| `explainer.html` tag nesting, `html.parser` | 0 errors; 8 sections, 42 details, 36 trees, 14 tables all balanced |
| `explainer.html` rendered in Chromium from `file://` | 0 non-`file://` requests, 0 console errors, 0 page errors, no horizontal overflow at 1280px, light and dark both render |
| The `pandas` and `networkx` snippet in `sample/README.md` | Runs verbatim from the repository root, exits 0, prints `62 83` as the comment claims |
| The four worked queries in `sample/README.md` | Each documented result table reproduced from `data.py` and compared row by row; all four match exactly |
| Anchor links in `families/README.md` | 42 links checked against the generated headings, 0 broken |
| Em dash search across the whole repository | 0 hits |
| `build/data.py` against the supplied file | md5 identical, moved unchanged |

## Judgement calls

Each with a one-line reason.

1. **Package contents sit at the repository root, not inside a `dcg/` subdirectory.** The layout in
   the brief shows `dcg/` as the top folder, but the same brief says the build runs from the
   repository root as `python3 build/build.py`; putting the contents at the root satisfies the
   command, and the zip wraps them in a `dcg/` folder so the archive still extracts to the layout
   shown.
2. **`families/README.md` and `sample/README.md` are generated, not hand-authored.** Both contain
   content derived from `data.py` (the 42 row index table, the column lists, the row counts), and
   the brief requires derived content to be generated; the static prose for both lives in
   `build/build.py`.
3. **`README.md` and this file are hand-authored.** Neither derives its content from `data.py`, and
   the brief allows the choice.
4. **Tree suffix order is `[node type] {properties} ~> cross-reference`.** The brief lists them in
   that order, and putting the cross-reference last makes it a suffix, as asked.
5. **Node type codes are expanded in the rendered trees.** `comp` is printed as `[component]` using
   `data.NODE_TYPE_NAMES`, because the trees are read by lawyers as well as engineers. The raw
   codes stay visible in the HTML legend and in the CSS class names.
6. **The C4 edge label `no CAF:` is rendered in parentheses like every other edge label.** It reads
   slightly oddly as `(no CAF:)`, but a consistent rule beats a special case, and the label is
   `data.py` content that must not be rewritten.
7. **The markdown terminology blocks use the `Term` then `: definition` convention.** That is the
   pandoc and kramdown definition-list syntax the brief asks for; GitHub does not render it as a
   `<dl>`, so it displays as two plain lines. It is still the correct source form.
8. **Terminology level labels are taken verbatim from `data.py` and differ between families.** C1
   uses Master, Participation, Component, Change, Order; C4 uses Anchor, Shared terms, Order; C8
   uses Bid layer, Conditions, Order. They were not normalised, because the labels carry meaning.
9. **Overlays appear in the `families/README.md` index table with category `Overlay`.** The brief
   asks for an index of the family files, and `overlays.md` is one of them.
10. **`details` elements are used only for families and overlays.** Nothing else on the page uses
    one, so the count stays at exactly 42, which is itself asserted by the build.
11. **The expand-all and collapse-all buttons are injected by JavaScript.** They do nothing without
    it, so with JavaScript disabled they are simply absent rather than present and inert. Every
    `details` block works natively either way.
12. **The strata navigation is a `nav` with an ordered list, L4 first in the DOM.** Reading order
    and visual order match, and the tonal steps darken toward L0 because master data is the
    bedrock.
13. **The `LOAD CSV` loader in `sample/README.md` targets Neo4j 5.26 or later.** Dynamic labels and
    relationship types are needed to load 22 labels and 33 types from two files; the APOC fallback
    for earlier versions is given alongside.
14. **Aliases were deduplicated on the full row only, as instructed.** No rows were removed: all 367
    rows are already unique as full rows. The intentional duplicate alias strings survive, including
    Partner Agreement under both C10 and S4, and SPA and DPA with their collision notes.
15. **The invariant walk is implemented as a recursive parent walk with cycle protection**, over
    `forms_part_of`, `accedes_to`, `governed_by` and `placed_under`, and it reports direct against
    inherited satisfaction separately, as asked.
16. **A two-line `.gitignore` was added, which is not in the specified layout.** Importing
    `build/data.py` from anywhere other than the build creates `build/__pycache__`, and committing
    compiled bytecode into a published standard would be a defect; `build/build.py` also sets
    `sys.dont_write_bytecode` so its own runs leave nothing behind.
17. **`dcg-v0.1.0.zip` wraps the package in a `dcg/` folder.** The archive extracts to exactly the
    directory layout in the brief. It contains 21 files and excludes `.git` and any `__pycache__`.
    File timestamps in the archive are fixed, so the zip is reproducible too.

## Conflicts between the brief and data.py

The rule applied was: `data.py` wins for content, the brief wins for structure and formatting.

1. **DOC-OF1 carries no party edges.** The brief says of the sample that "the signed order forms
   carry the party edges", in the plural. In `data.py` only `DOC-OF2` has `PARTY_TO` edges;
   `DOC-OF1`, the superseded 2023 order form, has none, and its `governed_by` parent `DOC-SMSA` is
   exempt shared terms, so the inheritance walk dead-ends. Adding an edge would have meant inventing
   content and would also have broken the asserted count of 83 edges. `data.py` therefore wins:
   `DOC-OF1` is recorded in `build/build.py` as a single named exemption with its reason, printed as
   a warning on every build, and listed as TODO 1 below. Every other master, participation and work
   instrument satisfies the invariant directly.
2. **oneNDA's status is `adopt_form`, not `adopt`.** The brief groups oneNDA inside the adopt list
   as "oneNDA as the O3 form". `data.py` gives it its own status value, `adopt_form`. The standards
   table in `explainer.html` is grouped by the `data.py` status, so oneNDA appears under its own
   heading, "Adopt as the standard form". The content is unchanged either way.
3. **The count of 36 families and the 39 rows in `families.csv`.** The brief asks for exactly 36
   families and separately asks for C0, S0 and V0 rows to be appended to `families.csv`. Both are
   satisfied: the assertion counts `data.FAMILIES`, and the CSV carries 39 rows. The extra three
   rows are reported explicitly in the build output so the difference is never a surprise.
4. **Prose that exists only in the brief.** The eight master data principles, the five layer
   one-liners, the degradation ladder wording, the catch-all process steps, the standards status
   labels and the cross-category call-outs are written out in the brief but are not in `data.py`.
   They are held as named constants at the top of `build/build.py` so that they are still generated
   from one place and are easy to move into `data.py` later. See TODO 4.

## TODO: what I believe is missing from data.py

Nothing below was improvised into the package. Each item is a gap I would want closed before v0.2.

1. **`DOC-OF1` has no `PARTY_TO` edges.** The sample is meant to demonstrate the invariant and
   currently contains one node that does not satisfy it. Two `PARTY_TO` edges from `DOC-OF1` to
   `LE-DH` and `LE-SAAS` would close it, at the cost of moving the sample edge count from 83 to 85.
   Alternatively `DOC-OF1` could be dropped, which would lose the supersedes chain the V1 family
   exists to show. My recommendation is to add the two edges and update the expected count.
2. **Overlay O4 has no alias rows.** Every other overlay is represented in the alias dictionary; O4
   (codes and policies) is not, although the overlay description names the documents. Supplier Code
   of Conduct, Code of Conduct, ESG Policy and Anti-Bribery Policy would be the obvious additions,
   which would move the alias count off 367.
3. **`sali_iri` is `pending mapping` on all 39 rows of `families.csv`.** Expected at v0.1 and
   already on the roadmap, but it means the SALI adoption claim is currently a commitment rather
   than a mapping.
4. **The narrative content lives in the brief, not in `data.py`.** If `data.py` is to be the single
   source of truth, then the eight principles, the five layer definitions, the invariant text, the
   catch-all process, the standards status labels and the cross-category call-outs should move into
   it as data. They are currently constants in `build/build.py`; the invariant in particular is
   quoted in three places and should have exactly one home.
5. **Seven node types never appear in the sample**: `incoterm`, `identifier_scheme`, `group`,
   `evidence`, `security`, `order_response` and `invoice`. The first two are reference data, the
   rest carry real modelling weight. A guarantee node (O1) and an order acknowledgement would each
   earn their place.
6. **Twenty-seven edge types never appear in the sample.** Three of them are called out in the
   explainer as the edges that justify the whole model and are not demonstrated anywhere:
   `mirrors` and `gap` (S10 back-to-back), and `limits` (V10 credit insurance). `secures` (O1) and
   `conflicts_with` (C4 battle of the forms) are the next two I would add.
7. **No worked example of a provisional entity.** The invariant says that where party resolution
   fails the edge points at a provisional entity flagged for review, never at nothing. There is no
   such node in the sample, so the most important failure path in the standard is undemonstrated.
8. **No unclassified document in the sample.** C0, S0 and V0 exist in the registry, but the sample
   contains no node with `status: provisional`, a `function_tag` and a `confidence` score, so the
   catch-all is described but not shown.
9. **`data.py` carries no licence or provenance metadata.** It has `VERSION` only. A licence field
   and a source note would let the build stamp both rather than relying on prose.
10. **Two properties in `PROPERTIES` describe edges, not nodes** (`captured_at` and
    `partner_function` are marked `edge: ...` in `applies_to`), which is correct but means
    `properties.csv` mixes node and edge properties in one registry without a column to separate
    them. A `level` column would make it machine-readable.

## Things checked and found correct

Recorded so that a reviewer does not have to re-derive them.

- All 40 non-blank `family_hint` values in `aliases.csv` resolve to a family or overlay code.
- All 22 sample node labels map, CamelCase to snake_case, onto a `node_types` id.
- All 33 sample edge types lowercase onto an `edge_types` id.
- All 166 sample edge endpoints resolve to a sample node.
- All 4 sample orders carry an `ordered_by` edge.
- All 19 standards URLs appear in `explainer.html` as plain anchors and nothing else; the page makes
  zero network requests.
- The tree renderer handles every mid-list depth reset in the data: C4 and C8 return to depth 1
  after a subtree, C13, S9, S11, S12, V6 and V10 do the same, and C11 nests five deep.

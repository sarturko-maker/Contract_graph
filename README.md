# Distributor Contract Graph (DCG) v0.1.0

DCG is an open standard for modelling contract knowledge as a graph in B2B distribution. It sets
out five layers, a nine-type master data spine, thirty-six contract families across three
categories, six overlays that cut across all of them, and registries of node types, edge types,
properties, aliases and external standards. It is deliberately narrow: it says how to shape the
graph, not which software to build it in.

It is written for two audiences at once. An in-house legal team should be able to read the family
tests and recognise its own filing cabinet. A data science team should be able to read the
registries and the sample graph and load them the same afternoon. Where a term belongs to one side
only, it is glossed for the other: a deed is an instrument with stricter execution formalities, and
a DAG is a directed graph with no cycles.

## The survival invariant

> Every contract node carries, from the moment it enters the graph, party-to edges pointing at
> entity_id for each signatory (ours and theirs) and, where it governs or constitutes trading, a
> governs or ordered-by edge pointing at account_id. Enforcement is at ingestion: where party
> resolution fails, the edge points at a provisional entity flagged for review, never at nothing.
> Amendments and schedules inherit party edges from their structural parent. Degradation ladder:
> full family classification plus content; else function tag only; else party and account edges
> plus dates. The worst case is still a working graph, and everything else is enrichment.

Everything else in this standard is optional. That one rule is not.

## The five layers

**L0 reference** holds the closed lists that everything points at: countries, currencies,
incoterms, classification codes and identifier schemes.

**L1 master data** holds the spine: legal entities, identifiers, relationships, accounts, sites,
products, people, org units and groups, with our side and theirs modelled identically and separated
by an is_ours flag.

**L2 agreement** holds one node per legal instrument that can change independently, joined by
structural edges that build the tree, lifecycle edges that change nodes over time and reference
edges that cut across branches.

**L3 content** holds what the paper says: clauses with stable identifiers, SALI classifications,
bi-temporal term facts and ODRL-shaped obligations.

**L4 transaction** holds orders, order responses, invoices and claims, in UBL shapes, attached to
the lowest node that actually governs them.

The relationship node sits on the L1 and L2 boundary: anchored in master data, used by the
agreement layer. Category (customer, supplier, vendor) is a property of the relationship, never of
the legal entity, so one real-world party can hold all three at once through three relationship
nodes.

## Reading order

**Legal.** Start at the invariant above, then `families/README.md` for the index and the family
test doctrine, then the category file that matches your day job. `registries/aliases.csv` is the
one to keep open while reading: 367 cover-page titles mapped to node types and family hints.

**Data science.** Start at the eight principles and the nine entity types in `explainer.html`, then
`registries/node_types.csv` and `registries/edge_types.csv`, then `sample/` for a 62 node, 83 edge
graph with load instructions and four worked queries.

**Everyone.** `explainer.html` is the whole standard on one self-contained page. It opens offline
from the file system, needs no network and needs no JavaScript.

## Directory map

```
README.md            what DCG is, the invariant, the layers, how to regenerate
explainer.html       the whole standard on one self-contained page
BUILD-REPORT.md      validation output, counts, judgement calls, open TODOs
build/
  data.py            the single source of truth
  build.py           the generator, Python 3 standard library only
families/
  README.md          index table, the family test doctrine, the catch-all process
  customers.md       C1 to C13
  suppliers.md       S1 to S12
  vendors.md         V1 to V11
  overlays.md        O1 to O6
registries/
  node_types.csv     29 node types by layer
  edge_types.csv     60 edge types with direction rules and time properties
  families.csv       36 families plus the C0, S0 and V0 catch-all rows
  aliases.csv        367 cover-page titles mapped to node types and family hints
  properties.csv     28 properties with allowed values
  overlays.csv       6 overlays
  standards_map.csv  19 external standards by status, drops included
sample/
  nodes.csv          62 nodes, neo4j-admin import headers
  edges.csv          83 edges
  README.md          what it shows, how to load it, four worked queries
```

## The five classifying properties

Family membership is decided by structure, never by the title on the cover. Five properties on
master-level nodes carry the tests:

| Property | Allowed values | The question it answers |
| --- | --- | --- |
| `scope` | global, regional, single, group_referenced | Does the master itself contemplate multi-entity adoption? |
| `paper` | ours, theirs, hybrid, model_form | Whose base document is it? |
| `commercial_completeness` | yes, no | Does an order alone complete a contract on pre-agreed commercials? |
| `commitment` | none, volume, target, exclusivity | What binding commercial commitment does the master carry? |
| `appointment` | yes, no | Does the agreement confer channel status? |

The title on the cover is recorded as an alias and used as a hint, never as a decision.

## Standards adopted

One line each. The full table, including the dropped candidates and the reason for each drop, is in
`registries/standards_map.csv`.

- **SALI LMSS** (SALI Alliance): IRIs for document types, clause components and player roles.
- **UBL, ISO/IEC 19845** (OASIS and ISO): order, order response, despatch advice and invoice shapes.
- **Concerto** (Accord Project, Linux Foundation): typed deal-point models per family.
- **ODRL** (W3C Recommendation): duty, permission and prohibition shape with obligor and obligee.
- **oneNDA**: adopted as the canonical standard-form node for the O3 pre-contract overlay.
- **LEI, ISO 17442, and GLEIF relationship data** (GLEIF): entity identifiers and the open
  parent-subsidiary graph.
- **GS1 GLN and GTIN** (GS1): site and product identifier schemes.
- **UNSPSC or ETIM**: classification codes on product nodes.
- **ISO 3166, 4217, 6523 and 8000**: countries, currencies, the identifier scheme registry and
  master data quality.

Adopted as patterns rather than as technology: **FINOS CDM** lifecycle events, and the **Akoma
Ntoso** eId naming convention for stable clause identifiers. **CUAD** is used as an extraction test
set and is not part of the standard. **OCDS** is available as an optional adapter for C11 public
sector frameworks. **DUNS** is noted and stored as one identifier scheme among several, never as a
primary key. **WorldCC** most-negotiated-terms research sets the priority order for extraction work.
Four candidates were considered and dropped: LegalRuleML, DPV, LEDGAR, and the Common Paper and
Bonterms standard forms. The reasons are in the registry, because a standard that names what it
rejected is easier to trust than one that lists only what it likes.

## Versioning

Semantic versioning. This is **v0.1.0**: the shape is settled, the SALI IRI mapping is not, and
family codes are stable from here. A new family or a new edge type is a minor version. Renaming or
removing a family code, an edge type or a property is a major version. Adding aliases, fixing prose
or extending the sample is a patch.

## Regeneration

Everything derived from `build/data.py` is generated. From the repository root:

```bash
python3 build/build.py
```

Python 3 standard library only, no installs, deterministic output: running it twice produces
identical files. The build validates as it goes and exits non-zero on any error. See
`BUILD-REPORT.md` for the output of the last run.

## Publication note

Proposed licence: **CC BY 4.0** for the text and the registries. This is a proposal to confirm
before release, not a licence grant. Nothing here is legal advice, and the sample graph is
illustrative: the entity names are invented and no real trading data appears in it.

## Roadmap, phase 2

- **Concerto deal-point models per family**: a typed model of the terms each family is expected to
  carry, so that extraction can be validated structurally rather than by eye.
- **ERP adapter mappings**: SAP business partner, KNVP partner functions and MARA material master;
  Oracle TCA parties and accounts. The spine was designed against these, and the mapping should be
  written down rather than rediscovered per implementation.
- **The SALI IRI mapping pass**: every row in `families.csv` currently reads `pending mapping`.
- **The OCDS adapter** for C11, where authority-side procurement data is published openly.
- **A query pattern library** in Cypher and SPARQL, generalising the four worked queries in
  `sample/README.md` into the questions each family is built to answer.

Corrections and new-family proposals are more useful than agreement. A family that does not survive
contact with a real filing cabinet should be challenged.

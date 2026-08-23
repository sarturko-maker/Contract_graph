# Worked sample graph

A worked graph, small enough to read in one sitting and large enough to show the shapes that
matter. Sixty-two nodes and eighty-three edges, generated from build/data.py by build/build.py.
It is illustrative: the entity names are invented and no real trading data appears here.

## What the sample shows

**One customer family end to end (C1)**

GlobalCo: a global master with two participations, one signed (Germany) and one deemed
(Netherlands), a superseding pricing schedule, a global amendment and a local amendment that
both bite on the same clause, and purchase orders hanging off the participations.

**One supplier family with a special pricing agreement (S1 and S9)**

VendorCo: an authorised distribution agreement with territory, price list and programme
components, and a special pricing agreement whose references edge crosses out of the supplier
tree into the customer relationship. A ship-and-debit claim hangs off the agreement.

**One vendor family (V1)**

SaaSCo: shared terms on the vendor's paper by URL with a capture date, two order forms with a
supersedes chain between them, a data processing agreement and a security addendum that prevails
over the shared terms.

**The master data spine**

Legal entities on both sides with an is_ours flag, an ownership hierarchy, LEI identifier
claims, accounts held with our org units and belonging to their entities, a ship-to site, a
product with a manufacturer and a classification, and a signatory.

**The survival invariant**

Every master, participation and work instrument reaches a signatory entity, directly or through
its structural parent, and every order reaches an account. The build fails if that stops being
true.

## Files

| File | Rows | Columns |
| --- | --- | --- |
| nodes.csv | 62 | `id:ID`, `name`, `:LABEL`, `layer`, `appointment`, `captured_at`, `category`, `claim_date`, `commercial_completeness`, `country`, `currency`, `effective_from`, `eid`, `family`, `flow_down`, `function`, `governing_law`, `is_ours`, `jurisdiction`, `modality`, `mpn`, `order_date`, `paper`, `payment_terms`, `recorded_at`, `role`, `sali_tag`, `scheme`, `scope`, `status`, `time_limited`, `type`, `valid_from`, `valid_to`, `value`, `version` |
| edges.csv | 83 | `:START_ID`, `:END_ID`, `:TYPE`, `captured_at`, `effective_from`, `function`, `role`, `their_part_no`, `valid_from`, `version` |

The headers follow the neo4j-admin import convention: `id:ID` is the node key and is also stored
as a property called id, `:LABEL` is the node label, `:TYPE` is the relationship type, and the
remaining columns are properties. A blank cell means the property does not apply to that row,
and the property is simply not set.

## Loading the sample

### Neo4j, bulk import

The fastest route, and the one to use for a fresh database. Stop the database first; bulk import
writes store files directly. Run from the repository root:

```bash
neo4j-admin database import full \
  --nodes=sample/nodes.csv \
  --relationships=sample/edges.csv \
  --id-type=string \
  --overwrite-destination \
  dcg
```

Then start the database and point your session at it. On Neo4j 4.x the command is `neo4j-admin
import` with `--database=dcg` instead of the trailing database name.

### Neo4j, LOAD CSV

Use this against a running database, for example when you cannot stop it or you are adding the
sample alongside other data. Copy both CSVs into the database import directory first. Dynamic
labels and types need Neo4j 5.26 or later:

```cypher
LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
CALL (row) {
  CREATE (n:$(row[':LABEL']))
  SET n += row
  SET n.id = row['id:ID']
  REMOVE n.`id:ID`, n.`:LABEL`
} IN TRANSACTIONS OF 500 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///edges.csv' AS row
MATCH (a {id: row[':START_ID']}), (b {id: row[':END_ID']})
CALL (row, a, b) {
  CREATE (a)-[r:$(row[':TYPE'])]->(b)
  SET r += row
  REMOVE r.`:START_ID`, r.`:END_ID`, r.`:TYPE`
} IN TRANSACTIONS OF 500 ROWS;
```

LOAD CSV reads an empty field as null, and setting a property to null removes it, so `SET n +=
row` gives exactly the blank-cell behaviour the files assume. On versions before 5.26 the
dynamic label and type are not available: use `apoc.create.node([row[':LABEL']], props)` and
`apoc.create.relationship(a, row[':TYPE'], props, b)`, or write one loader per label. The MATCH
on the edge pass has no label, so it scans every node; that is fine for sixty-two nodes and
wrong for a real graph, where you would index id per label first.

### pandas and networkx

For the data science side, the same two files load into a directed multigraph in a dozen lines.
A multigraph allows more than one edge between the same pair of nodes, which this model needs: a
change can both form part of a master and amend one of its clauses.

```python
import pandas as pd
import networkx as nx

nodes = pd.read_csv("sample/nodes.csv", dtype=str).fillna("")
edges = pd.read_csv("sample/edges.csv", dtype=str).fillna("")

G = nx.MultiDiGraph()
for row in nodes.to_dict("records"):
    props = {k: v for k, v in row.items() if v != ""}
    G.add_node(row["id:ID"], label=row[":LABEL"], **props)

for row in edges.to_dict("records"):
    props = {k: v for k, v in row.items()
             if v != "" and k not in (":START_ID", ":END_ID", ":TYPE")}
    G.add_edge(row[":START_ID"], row[":END_ID"], key=row[":TYPE"], **props)

print(G.number_of_nodes(), G.number_of_edges())  # 62 83

# the invariant, checked in four lines: walk structural parents until a party edge appears
STRUCTURAL = {"FORMS_PART_OF", "ACCEDES_TO", "GOVERNED_BY", "PLACED_UNDER"}

def reaches_a_party(node, seen=None):
    seen = seen or set()
    if node in seen:
        return False
    seen.add(node)
    out = list(G.out_edges(node, keys=True))
    if any(k == "PARTY_TO" for _, _, k in out):
        return True
    return any(reaches_a_party(t, seen) for _, t, k in out if k in STRUCTURAL)

for n, attrs in G.nodes(data=True):
    if attrs["label"] in ("Master", "Participation", "WorkInstrument"):
        print(n, attrs["label"], reaches_a_party(n))
```

Run as it stands, that last loop prints True for every node except DOC-OF1, the superseded 2023
order form. That is a real gap in the sample rather than a bug in the walk: data.py gives party
edges to the current order form only, and DOC-OF1's governed-by parent is shared terms on the
vendor's paper, which carries no party edges of its own. It is recorded as a named exemption in
the build and as a TODO in BUILD-REPORT.md.

## Four worked queries

Each query below runs against the loaded sample and returns exactly the rows shown. They are
ordered from the everyday question to the one that justifies the whole model.

### 1. From a purchase order to the agreement that governs it

The everyday question. An order number arrives; what did we actually agree, and with whom. It
walks ordered-by into master data, belongs-to to the counterparty entity, and up through
accedes-to to the master.

```cypher
MATCH (o:Order {id: 'TX-PO-4471'})-[:ORDERED_BY]->(a:Account)-[:BELONGS_TO]->(buyer:LegalEntity)
MATCH (o)-[:PLACED_UNDER]->(p:Participation)-[:ACCEDES_TO]->(m:Master)
RETURN o.name AS order, a.name AS account, buyer.name AS buyer,
       p.name AS participation, p.status AS participation_status,
       m.name AS governing_master, m.governing_law AS law;
```

Expected result:

| order | account | buyer | participation | participation_status | governing_master | law |
| --- | --- | --- | --- | --- | --- | --- |
| PO 4471 | Account 10001 GlobalCo GmbH | GlobalCo GmbH | LPA Germany 2021 | signed | Global MSA 2021 | England |

One row. Change the order id to TX-PO-5100 and the same query returns the Netherlands
participation, status deemed, under the same master.

### 2. Which participations vary a master clause

The C1 question that folder structures cannot answer. Clause 14 is the cap on liability; the
global amendment changes it for everyone, and a local amendment changes it again for one
country.

```cypher
MATCH (c:Clause {id: 'CL-MSA-14'})<-[r:VARIES|AMENDS]-(ch:Change)
OPTIONAL MATCH (ch)-[:FORMS_PART_OF]->(parent)
RETURN c.name AS clause, type(r) AS edge, ch.name AS instrument,
       labels(parent)[0] AS parent_type, parent.name AS parent, parent.status AS status
ORDER BY edge, instrument;
```

Expected result:

| clause | edge | instrument | parent_type | parent | status |
| --- | --- | --- | --- | --- | --- |
| MSA clause 14 cap on liability | AMENDS | Amendment 1 (2022) | Master | Global MSA 2021 | active |
| MSA clause 14 cap on liability | VARIES | Local amendment 1 (2023) | Participation | LPA Germany 2021 | signed |

Two rows. The second is the answer to the question the legal team actually asks: Germany has
varied the group cap, the Netherlands has not.

### 3. Claims under special pricing agreements, by customer relationship

The cross-category walk. The claim is a supplier-side transaction, the pricing agreement is a
supplier-side instrument, and the customer it was won for sits in a different category entirely.

```cypher
MATCH (claim:Claim)-[:CLAIMED_UNDER]->(spa:Change)-[:REFERENCES]->(rel:Relationship)
MATCH (spa)-[:FORMS_PART_OF]->(supplier_master:Master)
OPTIONAL MATCH (spa)-[:COVERS_PRODUCT]->(prod:Product)
RETURN claim.name AS claim, claim.claim_date AS claim_date, spa.name AS pricing_agreement,
       spa.valid_to AS expires, supplier_master.name AS supplier_agreement,
       rel.name AS customer_relationship, rel.category AS category, prod.name AS product;
```

Expected result:

| claim | claim_date | pricing_agreement | expires | supplier_agreement | customer_relationship | category | product |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Ship-and-debit claim 0007 | 2026-03-02 | SPA customer GlobalCo project Falcon | 2026-12-31 | Distribution agreement 2018 | GlobalCo customer relationship | customer | SKU CBL-001 LV cable |

One row, and it spans two relationships in two categories. This is the walk that justifies a
graph rather than a document management system.

### 4. The liability cap in force on a given date

The bi-temporal demonstration. Term facts carry valid_from and valid_to for when the fact was
true in the world, and recorded_at for when the graph learned it. The supersedes chain links the
old fact to the new one.

```cypher
UNWIND [date('2024-05-01'), date('2024-07-01')] AS as_at
MATCH (:Clause {id: 'CL-MSA-14'})-[:HAS_TERM]->(t:TermFact)
WHERE date(t.valid_from) <= as_at
  AND (t.valid_to IS NULL OR t.valid_to = '' OR date(t.valid_to) >= as_at)
RETURN as_at, t.name AS cap_in_force, t.valid_from AS valid_from,
       t.valid_to AS valid_to, t.recorded_at AS recorded_at
ORDER BY as_at;
```

Expected result:

| as_at | cap_in_force | valid_from | valid_to | recorded_at |
| --- | --- | --- | --- | --- |
| 2024-05-01 | liability cap = 12 months' charges | 2021-03-01 | 2024-05-31 | 2026-01-15 |
| 2024-07-01 | liability cap = 24 months' charges | 2024-06-01 | (null) | 2026-01-15 |

Two rows from one query. Both facts were recorded on the same day in 2026, which is the second
axis: the graph learned in 2026 what had been true since 2024. To walk the chain explicitly, add
MATCH (new:TermFact)-[:SUPERSEDES]->(old:TermFact).

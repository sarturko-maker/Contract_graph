#!/usr/bin/env python3
"""Build the Distributor Contract Graph (DCG) package from build/data.py.

Run from the repository root:

    python3 build/build.py

Everything derived from data.py is written by this script: families/,
registries/, sample/ and explainer.html. Nothing here paraphrases or trims
data.py; it only arranges it. Output is deterministic, so running the script
twice produces byte-identical files.
"""

import csv
import html
import io
import re
import sys
import textwrap
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parent
ROOT = BUILD_DIR.parent
sys.path.insert(0, str(BUILD_DIR))
sys.dont_write_bytecode = True  # keep build/ free of a __pycache__ directory

import data  # noqa: E402

# ---------------------------------------------------------------------------
# expected counts, asserted at the end of the build
# ---------------------------------------------------------------------------

EXPECTED = {
    "families": 36,
    "overlays": 6,
    "node_types": 29,
    "edge_types": 60,
    "aliases": 367,
    "properties": 28,
    "standards": 19,
    "sample_nodes": 62,
    "sample_edges": 83,
}

CATEGORIES = [
    ("Customers", "customers.md", "C"),
    ("Suppliers", "suppliers.md", "S"),
    ("Vendors", "vendors.md", "V"),
]

EDGE_KIND_NAMES = {
    "s": "structural",
    "l": "lifecycle",
    "t": "transactional",
    "e": "evidence",
    "": "",
}

# The catch-all rows appended to families.csv. Each category carries an X0
# family so that an unclassifiable document still has somewhere to live.
CATCH_ALL_ROWS = [
    ("C0", "Unclassified customer document", "Customers"),
    ("S0", "Unclassified supplier document", "Suppliers"),
    ("V0", "Unclassified vendor document", "Vendors"),
]

CATCH_ALL_TEST = (
    "Catch-all. The document is on the {cat_lower} side of the house but its structure does not "
    "match any family test, or the evidence is too thin to decide. It still gets a function tag "
    "from the closed list (governs, transacts, changes, secures, evidences, resolves, "
    "enables_channel, pre_contract), attaches to its relationship with status provisional and a "
    "confidence score, and enters the human review queue."
)

CATCH_ALL_PROPS = (
    "function_tag: governs, transacts, changes, secures, evidences, resolves, enables_channel or "
    "pre_contract | status: provisional | confidence: 0.00 to 1.00"
)

CATCH_ALL_COMPLEXITY = (
    "Reviewer outcomes feed the alias dictionary; recurring clusters become new-family proposals; "
    "the metric is unclassified rate per category, trending down."
)

# The one node in the worked sample that the invariant walk cannot satisfy.
# data.py is the source of truth for content, so the gap is recorded here as a
# named exemption rather than papered over by inventing an edge.
INVARIANT_EXEMPTIONS = {
    "DOC-OF1": (
        "Superseded 2023 order form. data.py gives party edges to the current order form "
        "(DOC-OF2) only, and DOC-OF1's governed-by parent DOC-SMSA is exempt shared terms. "
        "Logged in BUILD-REPORT.md as a data gap, not fixed by inventing an edge."
    ),
}

INVARIANT_SHARED_TERMS_NOTE = (
    "DOC-SMSA is shared terms on the vendor's paper, so it is exempt as a shared_terms node; "
    "the signed order form carries the party edges, which is the point the sample makes."
)

INHERITING_EDGES = ("FORMS_PART_OF", "ACCEDES_TO", "GOVERNED_BY", "PLACED_UNDER")

INVARIANT_TEXT = (
    "Every contract node carries, from the moment it enters the graph, party-to edges pointing at "
    "entity_id for each signatory (ours and theirs) and, where it governs or constitutes trading, "
    "a governs or ordered-by edge pointing at account_id. Enforcement is at ingestion: where party "
    "resolution fails, the edge points at a provisional entity flagged for review, never at "
    "nothing. Amendments and schedules inherit party edges from their structural parent. "
    "Degradation ladder: full family classification plus content; else function tag only; else "
    "party and account edges plus dates. The worst case is still a working graph, and everything "
    "else is enrichment."
)

PRINCIPLES = [
    ("Parties are legal entities, accounts are trading arrangements",
     "Contracts attach to entities and transactions to accounts. Mixing the two is the most common "
     "modelling error and the reason so many systems cannot answer who is actually bound."),
    ("Symmetry",
     "Our side and theirs use the same types, separated by an is_ours flag. There is no second "
     "schema for the house entities."),
    ("Identity is plural",
     "Identity is a set of scheme plus value claims, each with a source and a validity window, "
     "never one ID field."),
    ("Two hierarchies, never conflated",
     "Legal ownership (owns) and commercial grouping (member_of) are different edges. A buying "
     "group is not a parent company."),
    ("Roles are edges, not types",
     "Ship-to, bill-to, payer, signatory and guarantor are edges with properties. Creating a node "
     "type per role multiplies the model without adding information."),
    ("Time on every edge",
     "Every edge carries validity dates, and where the question is bi-temporal, recorded_at as the "
     "second axis: when the fact was true, and when the graph learned it."),
    ("The graph references, never masters",
     "ERP or MDM stays the system of record. Every node carries source_system and source_key, and "
     "the graph is rebuilt from them."),
    ("Minimal spine, open extensions",
     "Nine entity types carry the load. Anything else belongs in an extension, not in the spine."),
]

SPINE_IDS = [
    "legal_entity", "identifier", "relationship", "account", "site",
    "product", "person", "org_unit", "group",
]

SUB_LAYERS = [
    ("Structure", "Clause nodes with stable identifiers, using the Akoma Ntoso eId naming "
                  "convention (doc#cl_14), so that an amendment can point at a clause rather than "
                  "at a document."),
    ("Classification", "SALI LMSS IRIs on documents and clauses, applied through tagged-as edges. "
                       "One clause vocabulary, not several."),
    ("Terms", "Term facts: Concerto-typed extracted values, bi-temporal, with a supersedes chain "
              "so that the question is not what the cap is but what the cap was on a given date."),
    ("Obligations", "ODRL-shaped duties, permissions and prohibitions, each with obligor and "
                    "obligee edges back into master data, which is the invariant reappearing at "
                    "clause level."),
]

STATUS_LABELS = [
    ("adopt", "Adopt"),
    ("adopt_form", "Adopt as the standard form"),
    ("pattern", "Adopt the pattern"),
    ("test_set", "Test set, validation only"),
    ("optional_adapter", "Optional adapter"),
    ("note", "Noted, used with care"),
    ("research_input", "Research input"),
    ("dropped", "Dropped"),
]

STATUS_NOTES = {
    "adopt": "Taken as it stands and referenced normatively.",
    "adopt_form": "Adopted as the canonical form for the node it fills.",
    "pattern": "The shape is borrowed, the technology is not.",
    "test_set": "Used to validate extraction, not part of the standard.",
    "optional_adapter": "Available where the family calls for it, not required.",
    "note": "Recorded because it is everywhere, not because it is open.",
    "research_input": "Feeds the priority order for extraction work.",
    "dropped": "Considered and rejected, with the reason kept in the open.",
}

CROSS_CATEGORY_CALLOUTS = [
    ("S9 references", "references",
     "A special pricing agreement sits in the supplier tree but is priced for a named customer. "
     "The references edge runs from the supplier-side instrument to the customer relationship, "
     "which is how a ship-and-debit claim can be tied back to the customer it was won for."),
    ("S10 mirrors and gap", "mirrors, gap",
     "A back-to-back services subcontract mirrors the customer statement of work. The mirrors edge "
     "pairs them; the gap edge carries the delta as a property. That pair of edges is the risk "
     "register: everything we promised the customer that the subcontractor did not promise us."),
    ("V10 limits", "limits",
     "A credit insurance buyer limit is a component in the vendor tree that points, through a "
     "limits edge, at a customer account in master data. The finance side and the trading side "
     "meet on that edge."),
    ("S1 flows down to C10", "flows_down_to",
     "Vendor end-user terms accepted in the supplier tree have to reach the reseller customer. The "
     "flows-down-to edge crosses from a supplier-side shared terms node into the customer "
     "relationship, which no folder structure can show."),
]

CATCH_ALL_PROCESS = [
    "Assign a function tag from the closed list: governs, transacts, changes, secures, evidences, "
    "resolves, enables_channel, pre_contract. This is nearly always determinable from the first "
    "page.",
    "Attach the document to its relationship with status provisional and a confidence score.",
    "Put it in the human review queue, ordered by value at risk rather than by date.",
    "Feed the reviewer's outcome back into the alias dictionary, so the same cover page classifies "
    "itself next time.",
    "Where a cluster of unclassified documents recurs, raise it as a new-family proposal rather "
    "than stretching an existing test.",
    "Track unclassified rate per category as the standing metric, and expect it to trend down.",
]

REPO_MAP = [
    ("README.md", "What DCG is, the invariant, the layers, and how to regenerate."),
    ("explainer.html", "This page. Self-contained, no external requests."),
    ("BUILD-REPORT.md", "Validation output, counts, judgement calls and open TODOs."),
    ("build/data.py", "The single source of truth: families, overlays, registries, sample graph."),
    ("build/build.py", "The generator. Standard library only."),
    ("families/", "One markdown file per category, plus overlays and an index."),
    ("registries/", "Seven CSVs: node types, edge types, families, aliases, properties, overlays, "
                    "standards."),
    ("sample/", "A 62 node, 83 edge worked graph with load instructions and worked queries."),
]

# node type colours, one per type, consistent between legend and trees
NODE_TYPE_COLOURS = {
    "rel":    ("#6d3f9c", "#c6a6ea"),
    "master": ("#1a4f8a", "#8fb9e8"),
    "part":   ("#0f6355", "#5fc7b1"),
    "comp":   ("#7a5200", "#dcb45f"),
    "ch":     ("#a03a1f", "#f0a58f"),
    "wk":     ("#145e75", "#83cbdd"),
    "ord":    ("#41620f", "#acd06e"),
    "sh":     ("#6b4a2f", "#d0ad90"),
    "ev":     ("#4a5568", "#b6bfcc"),
    "sec":    ("#8f2245", "#ef95af"),
}

# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

REPORT = io.StringIO()


def say(line=""):
    """Print to the console and keep a copy for BUILD-REPORT.md."""
    print(line)
    REPORT.write(line + "\n")


def write_text(rel_path, text):
    path = ROOT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def write_csv(rel_path, header, rows):
    path = ROOT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)
    return path


def slug(text):
    """GitHub-style heading anchor."""
    out = text.lower()
    out = re.sub(r"[^a-z0-9 \-]", "", out)
    return out.strip().replace(" ", "-")


def first_sentence(text):
    """One-line extract: the first sentence of a family test."""
    match = re.search(r"^(.*?[.])(\s|$)", text.strip())
    sentence = match.group(1) if match else text.strip()
    return " ".join(sentence.split())


def esc(text):
    return html.escape(str(text), quote=True)


def wrap(text, width=96, indent=""):
    return textwrap.fill(" ".join(str(text).split()), width=width,
                         initial_indent=indent, subsequent_indent=indent)


# ---------------------------------------------------------------------------
# tree renderer, shared by markdown and HTML
# ---------------------------------------------------------------------------

def tree_rows(tree):
    """Turn (depth, edge_label, edge_kind, node_label, node_type, xref, prop)
    tuples into rows carrying box-drawing connectors.

    Last-sibling detection looks ahead: a node is the last of its siblings when
    no later node sits at the same depth before the depth drops below it. The
    ancestor prefix is rebuilt for every row, which is what makes mid-list depth
    resets (C4, C8, C13, S9, V10) render correctly.
    """
    depths = [row[0] for row in tree]
    count = len(depths)

    is_last = [True] * count
    for i, depth in enumerate(depths):
        for j in range(i + 1, count):
            if depths[j] < depth:
                break
            if depths[j] == depth:
                is_last[i] = False
                break

    rows = []
    for i, (depth, edge_label, edge_kind, node_label, node_type, xref, prop) in enumerate(tree):
        parts = []
        for level in range(1, depth):
            ancestor = None
            for j in range(i - 1, -1, -1):
                if depths[j] == level:
                    ancestor = j
                    break
            parts.append("    " if ancestor is None or is_last[ancestor] else "│   ")
        prefix = "".join(parts)
        if depth == 0:
            connector = ""
        else:
            connector = "└── " if is_last[i] else "├── "
        rows.append({
            "prefix": prefix,
            "connector": connector,
            "edge_label": edge_label,
            "edge_kind": edge_kind,
            "node_label": node_label,
            "node_type": node_type,
            "type_name": data.NODE_TYPE_NAMES.get(node_type, node_type),
            "xref": xref,
            "prop": prop,
        })
    return rows


def render_tree_text(tree):
    lines = []
    for row in tree_rows(tree):
        line = row["prefix"] + row["connector"]
        if row["edge_label"]:
            line += "(%s) " % row["edge_label"]
        line += row["node_label"]
        line += " [%s]" % row["type_name"]
        if row["prop"]:
            line += " {%s}" % row["prop"]
        if row["xref"]:
            line += " ~> %s" % row["xref"]
        lines.append(line.rstrip())
    return "\n".join(lines)


def render_tree_html(tree):
    lines = []
    for row in tree_rows(tree):
        out = ['<span class="tc">%s%s</span>' % (esc(row["prefix"]), esc(row["connector"]))]
        if row["edge_label"]:
            kind = row["edge_kind"] or "n"
            out.append('<span class="ek ek-%s" title="%s edge">(%s)</span> ' % (
                kind, esc(EDGE_KIND_NAMES.get(row["edge_kind"], "structural") or "root"),
                esc(row["edge_label"])))
        out.append('<span class="nd nt-%s">%s</span>' % (row["node_type"], esc(row["node_label"])))
        out.append(' <span class="ntag nt-%s">[%s]</span>' % (
            row["node_type"], esc(row["type_name"])))
        if row["prop"]:
            out.append(' <span class="pr">{%s}</span>' % esc(row["prop"]))
        if row["xref"]:
            out.append(' <span class="xr">~&gt; %s</span>' % esc(row["xref"]))
        lines.append("".join(out))
    return '<pre class="tree" tabindex="0">' + "\n".join(lines) + "</pre>"


# ---------------------------------------------------------------------------
# families/*.md
# ---------------------------------------------------------------------------

FAMILY_DOCTRINE = (
    "Family membership is decided by structure, never by the title on the cover. The question is "
    "always what the instruments do and how they hang together: is there a layer between the "
    "master and local trading, does an order alone complete a contract, does the agreement confer "
    "channel status. The title is recorded as an alias in registries/aliases.csv, where it is "
    "useful as a hint and never as a decision. Five classifying properties do the work at "
    "master level: scope, paper, commercial completeness, commitment and appointment."
)

FAMILY_README_INTRO = (
    "Thirty-six families across three categories: thirteen on the customer side, twelve on the "
    "supplier side, eleven on the vendor side. Category is a property of the relationship, not of "
    "the legal entity, so one real-world party can appear in all three lists through three "
    "relationship nodes. Six overlays cut across every family and are listed in overlays.md."
)


def family_markdown(family):
    out = []
    out.append("## %s. %s" % (family["code"], family["name"]))
    out.append("")
    out.append(wrap(family["test"]))
    out.append("")
    out.append("```")
    out.append(render_tree_text(family["tree"]))
    out.append("```")
    out.append("")
    out.append("### Terminology")
    out.append("")
    for level, terms in family["terms"]:
        out.append(level)
        out.append(": %s" % " ".join(terms.split()))
        out.append("")
    out.append("### Properties")
    out.append("")
    out.append(wrap(family["props"]))
    out.append("")
    out.append("### Complexity")
    out.append("")
    for item in family["complexity"]:
        out.append(wrap(item, width=94, indent="  ").replace("  ", "- ", 1))
    out.append("")
    return "\n".join(out)


def build_family_files():
    written = []
    for category, filename, _prefix in CATEGORIES:
        families = [f for f in data.FAMILIES if f["cat"] == category]
        singular = category.lower().rstrip("s")
        out = ["# %s families" % singular.capitalize(), ""]
        out.append(wrap(
            "%d families on the %s side. Each entry gives the family test, the tree, the "
            "terminology that turns up on real cover pages, the classifying properties and the "
            "complexity that makes the family worth separating."
            % (len(families), singular)))
        out.append("")
        for family in families:
            out.append(family_markdown(family))
        written.append(write_text("families/%s" % filename, "\n".join(out).rstrip() + "\n"))

    # overlays.md
    out = ["# Overlays", ""]
    out.append(wrap(
        "Six overlays cut across the families. An overlay is not a family: it is a set of node "
        "types and edges that can appear under any family tree, in any category. A guarantee "
        "secures obligations wherever they arise; a data processing agreement forms part of "
        "whatever master it was signed under."))
    out.append("")
    for overlay in data.OVERLAYS:
        out.append("## %s. %s" % (overlay["code"], overlay["name"]))
        out.append("")
        out.append(wrap(overlay["desc"]))
        out.append("")
        out.append("Node examples")
        out.append(": %s" % " ".join(overlay["nodes"].split()))
        out.append("")
        out.append("Key edges")
        out.append(": %s" % " ".join(overlay["edges"].split()))
        out.append("")
    written.append(write_text("families/overlays.md", "\n".join(out).rstrip() + "\n"))

    # families/README.md
    out = ["# Family index", ""]
    out.append(wrap(FAMILY_README_INTRO))
    out.append("")
    out.append("| Code | Name | Category | Test, first line |")
    out.append("| --- | --- | --- | --- |")
    file_by_cat = {cat: fn for cat, fn, _ in CATEGORIES}
    for family in data.FAMILIES:
        anchor = "%s#%s" % (file_by_cat[family["cat"]],
                            slug("%s. %s" % (family["code"], family["name"])))
        out.append("| [%s](%s) | %s | %s | %s |" % (
            family["code"], anchor, family["name"], family["cat"],
            first_sentence(family["test"]).replace("|", "\\|")))
    for overlay in data.OVERLAYS:
        anchor = "overlays.md#%s" % slug("%s. %s" % (overlay["code"], overlay["name"]))
        out.append("| [%s](%s) | %s | Overlay | %s |" % (
            overlay["code"], anchor, overlay["name"],
            first_sentence(overlay["desc"]).replace("|", "\\|")))
    out.append("")
    out.append("## The family test doctrine")
    out.append("")
    out.append(wrap(FAMILY_DOCTRINE))
    out.append("")
    out.append("## When nothing fits: the catch-all")
    out.append("")
    out.append(wrap(
        "Each category carries an X0 unclassified family (C0, S0 and V0 in "
        "registries/families.csv). A document that cannot be placed is not left out of the graph:"))
    out.append("")
    for step in CATCH_ALL_PROCESS:
        out.append(wrap(step, width=94, indent="  ").replace("  ", "- ", 1))
    out.append("")
    written.append(write_text("families/README.md", "\n".join(out).rstrip() + "\n"))
    return written


# ---------------------------------------------------------------------------
# registries/*.csv
# ---------------------------------------------------------------------------

def build_registries():
    written = []

    written.append(write_csv(
        "registries/node_types.csv",
        ["id", "name", "layer", "definition", "examples"],
        [list(row) for row in data.NODE_TYPES]))

    written.append(write_csv(
        "registries/edge_types.csv",
        ["id", "label", "kind", "from_types", "to_types", "direction_rule", "time_properties",
         "notes"],
        [list(row) for row in data.EDGE_TYPES]))

    family_rows = []
    for family in data.FAMILIES:
        family_rows.append([
            family["code"],
            family["name"],
            family["cat"],
            " ".join(family["test"].split()),
            " ".join(family["props"].split()),
            " ".join(" ".join(family["complexity"]).split()),
            "pending mapping",
        ])
    for code, name, category in CATCH_ALL_ROWS:
        family_rows.append([
            code,
            name,
            category,
            CATCH_ALL_TEST.format(cat_lower=category.lower().rstrip("s")),
            CATCH_ALL_PROPS,
            CATCH_ALL_COMPLEXITY,
            "pending mapping",
        ])
    written.append(write_csv(
        "registries/families.csv",
        ["code", "name", "category", "family_test", "key_properties", "complexity_summary",
         "sali_iri"],
        family_rows))

    # aliases: dedupe exact full-row duplicates only, keeping first appearance
    seen = set()
    alias_rows = []
    for row in data.ALIASES:
        key = tuple(row)
        if key in seen:
            continue
        seen.add(key)
        alias_rows.append(list(row))
    written.append(write_csv(
        "registries/aliases.csv",
        ["alias", "node_type", "family_hint", "notes"],
        alias_rows))

    written.append(write_csv(
        "registries/properties.csv",
        ["property", "applies_to", "allowed_values", "definition"],
        [list(row) for row in data.PROPERTIES]))

    written.append(write_csv(
        "registries/overlays.csv",
        ["code", "name", "description", "node_examples", "key_edges"],
        [[o["code"], o["name"], " ".join(o["desc"].split()), o["nodes"], o["edges"]]
         for o in data.OVERLAYS]))

    written.append(write_csv(
        "registries/standards_map.csv",
        ["slot", "standard", "steward", "status", "what_we_take", "adoption_evidence", "url"],
        [list(row) for row in data.STANDARDS]))

    return written, alias_rows, family_rows


# ---------------------------------------------------------------------------
# sample/
# ---------------------------------------------------------------------------

SAMPLE_INTRO = (
    "A worked graph, small enough to read in one sitting and large enough to show the shapes that "
    "matter. Sixty-two nodes and eighty-three edges, generated from build/data.py by "
    "build/build.py. It is illustrative: the entity names are invented and no real trading data "
    "appears here."
)

SAMPLE_SHOWS = [
    ("One customer family end to end (C1)",
     "GlobalCo: a global master with two participations, one signed (Germany) and one deemed "
     "(Netherlands), a superseding pricing schedule, a global amendment and a local amendment that "
     "both bite on the same clause, and purchase orders hanging off the participations."),
    ("One supplier family with a special pricing agreement (S1 and S9)",
     "VendorCo: an authorised distribution agreement with territory, price list and programme "
     "components, and a special pricing agreement whose references edge crosses out of the supplier "
     "tree into the customer relationship. A ship-and-debit claim hangs off the agreement."),
    ("One vendor family (V1)",
     "SaaSCo: shared terms on the vendor's paper by URL with a capture date, two order forms with a "
     "supersedes chain between them, a data processing agreement and a security addendum that "
     "prevails over the shared terms."),
    ("The master data spine",
     "Legal entities on both sides with an is_ours flag, an ownership hierarchy, LEI identifier "
     "claims, accounts held with our org units and belonging to their entities, a ship-to site, a "
     "product with a manufacturer and a classification, and a signatory."),
    ("The survival invariant",
     "Every master, participation and work instrument reaches a signatory entity, directly or "
     "through its structural parent, and every order reaches an account. The build fails if that "
     "stops being true."),
]

QUERIES = [
    {
        "title": "From a purchase order to the agreement that governs it",
        "why": "The everyday question. An order number arrives; what did we actually agree, and "
               "with whom. It walks ordered-by into master data, belongs-to to the counterparty "
               "entity, and up through accedes-to to the master.",
        "cypher": """MATCH (o:Order {id: 'TX-PO-4471'})-[:ORDERED_BY]->(a:Account)-[:BELONGS_TO]->(buyer:LegalEntity)
MATCH (o)-[:PLACED_UNDER]->(p:Participation)-[:ACCEDES_TO]->(m:Master)
RETURN o.name AS order, a.name AS account, buyer.name AS buyer,
       p.name AS participation, p.status AS participation_status,
       m.name AS governing_master, m.governing_law AS law;""",
        "expected": [
            ["order", "account", "buyer", "participation", "participation_status",
             "governing_master", "law"],
            ["PO 4471", "Account 10001 GlobalCo GmbH", "GlobalCo GmbH", "LPA Germany 2021",
             "signed", "Global MSA 2021", "England"],
        ],
        "note": "One row. Change the order id to TX-PO-5100 and the same query returns the "
                "Netherlands participation, status deemed, under the same master.",
    },
    {
        "title": "Which participations vary a master clause",
        "why": "The C1 question that folder structures cannot answer. Clause 14 is the cap on "
               "liability; the global amendment changes it for everyone, and a local amendment "
               "changes it again for one country.",
        "cypher": """MATCH (c:Clause {id: 'CL-MSA-14'})<-[r:VARIES|AMENDS]-(ch:Change)
OPTIONAL MATCH (ch)-[:FORMS_PART_OF]->(parent)
RETURN c.name AS clause, type(r) AS edge, ch.name AS instrument,
       labels(parent)[0] AS parent_type, parent.name AS parent, parent.status AS status
ORDER BY edge, instrument;""",
        "expected": [
            ["clause", "edge", "instrument", "parent_type", "parent", "status"],
            ["MSA clause 14 cap on liability", "AMENDS", "Amendment 1 (2022)", "Master",
             "Global MSA 2021", "active"],
            ["MSA clause 14 cap on liability", "VARIES", "Local amendment 1 (2023)",
             "Participation", "LPA Germany 2021", "signed"],
        ],
        "note": "Two rows. The second is the answer to the question the legal team actually asks: "
                "Germany has varied the group cap, the Netherlands has not.",
    },
    {
        "title": "Claims under special pricing agreements, by customer relationship",
        "why": "The cross-category walk. The claim is a supplier-side transaction, the pricing "
               "agreement is a supplier-side instrument, and the customer it was won for sits in a "
               "different category entirely.",
        "cypher": """MATCH (claim:Claim)-[:CLAIMED_UNDER]->(spa:Change)-[:REFERENCES]->(rel:Relationship)
MATCH (spa)-[:FORMS_PART_OF]->(supplier_master:Master)
OPTIONAL MATCH (spa)-[:COVERS_PRODUCT]->(prod:Product)
RETURN claim.name AS claim, claim.claim_date AS claim_date, spa.name AS pricing_agreement,
       spa.valid_to AS expires, supplier_master.name AS supplier_agreement,
       rel.name AS customer_relationship, rel.category AS category, prod.name AS product;""",
        "expected": [
            ["claim", "claim_date", "pricing_agreement", "expires", "supplier_agreement",
             "customer_relationship", "category", "product"],
            ["Ship-and-debit claim 0007", "2026-03-02", "SPA customer GlobalCo project Falcon",
             "2026-12-31", "Distribution agreement 2018", "GlobalCo customer relationship",
             "customer", "SKU CBL-001 LV cable"],
        ],
        "note": "One row, and it spans two relationships in two categories. This is the walk that "
                "justifies a graph rather than a document management system.",
    },
    {
        "title": "The liability cap in force on a given date",
        "why": "The bi-temporal demonstration. Term facts carry valid_from and valid_to for when "
               "the fact was true in the world, and recorded_at for when the graph learned it. The "
               "supersedes chain links the old fact to the new one.",
        "cypher": """UNWIND [date('2024-05-01'), date('2024-07-01')] AS as_at
MATCH (:Clause {id: 'CL-MSA-14'})-[:HAS_TERM]->(t:TermFact)
WHERE date(t.valid_from) <= as_at
  AND (t.valid_to IS NULL OR t.valid_to = '' OR date(t.valid_to) >= as_at)
RETURN as_at, t.name AS cap_in_force, t.valid_from AS valid_from,
       t.valid_to AS valid_to, t.recorded_at AS recorded_at
ORDER BY as_at;""",
        "expected": [
            ["as_at", "cap_in_force", "valid_from", "valid_to", "recorded_at"],
            ["2024-05-01", "liability cap = 12 months' charges", "2021-03-01", "2024-05-31",
             "2026-01-15"],
            ["2024-07-01", "liability cap = 24 months' charges", "2024-06-01", "", "2026-01-15"],
        ],
        "note": "Two rows from one query. Both facts were recorded on the same day in 2026, which "
                "is the second axis: the graph learned in 2026 what had been true since 2024. To "
                "walk the chain explicitly, add "
                "MATCH (new:TermFact)-[:SUPERSEDES]->(old:TermFact).",
    },
]


def sample_property_keys():
    node_keys = set()
    for _id, _name, _label, _layer, props in data.SAMPLE_NODES:
        node_keys.update(props)
    edge_keys = set()
    for _a, _t, _b, props in data.SAMPLE_EDGES:
        edge_keys.update(props)
    return sorted(node_keys), sorted(edge_keys)


def build_sample():
    written = []
    node_keys, edge_keys = sample_property_keys()

    node_header = ["id:ID", "name", ":LABEL", "layer"] + node_keys
    node_rows = []
    for node_id, name, label, layer, props in data.SAMPLE_NODES:
        node_rows.append([node_id, name, label, layer] + [props.get(k, "") for k in node_keys])
    written.append(write_csv("sample/nodes.csv", node_header, node_rows))

    edge_header = [":START_ID", ":END_ID", ":TYPE"] + edge_keys
    edge_rows = []
    for start, edge_type, end, props in data.SAMPLE_EDGES:
        edge_rows.append([start, end, edge_type] + [props.get(k, "") for k in edge_keys])
    written.append(write_csv("sample/edges.csv", edge_header, edge_rows))

    out = ["# Worked sample graph", ""]
    out.append(wrap(SAMPLE_INTRO))
    out.append("")
    out.append("## What the sample shows")
    out.append("")
    for title, body in SAMPLE_SHOWS:
        out.append("**%s**" % title)
        out.append("")
        out.append(wrap(body))
        out.append("")
    out.append("## Files")
    out.append("")
    out.append("| File | Rows | Columns |")
    out.append("| --- | --- | --- |")
    out.append("| nodes.csv | %d | %s |" % (len(node_rows), ", ".join("`%s`" % c for c in node_header)))
    out.append("| edges.csv | %d | %s |" % (len(edge_rows), ", ".join("`%s`" % c for c in edge_header)))
    out.append("")
    out.append(wrap(
        "The headers follow the neo4j-admin import convention: `id:ID` is the node key and is also "
        "stored as a property called id, `:LABEL` is the node label, `:TYPE` is the relationship "
        "type, and the remaining columns are properties. A blank cell means the property does not "
        "apply to that row, and the property is simply not set."))
    out.append("")

    out.append("## Loading the sample")
    out.append("")
    out.append("### Neo4j, bulk import")
    out.append("")
    out.append(wrap(
        "The fastest route, and the one to use for a fresh database. Stop the database first; "
        "bulk import writes store files directly. Run from the repository root:"))
    out.append("")
    out.append("```bash")
    out.append("neo4j-admin database import full \\")
    out.append("  --nodes=sample/nodes.csv \\")
    out.append("  --relationships=sample/edges.csv \\")
    out.append("  --id-type=string \\")
    out.append("  --overwrite-destination \\")
    out.append("  dcg")
    out.append("```")
    out.append("")
    out.append(wrap(
        "Then start the database and point your session at it. On Neo4j 4.x the command is "
        "`neo4j-admin import` with `--database=dcg` instead of the trailing database name."))
    out.append("")
    out.append("### Neo4j, LOAD CSV")
    out.append("")
    out.append(wrap(
        "Use this against a running database, for example when you cannot stop it or you are "
        "adding the sample alongside other data. Copy both CSVs into the database import "
        "directory first. Dynamic labels and types need Neo4j 5.26 or later:"))
    out.append("")
    out.append("```cypher")
    out.append("""LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
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
} IN TRANSACTIONS OF 500 ROWS;""")
    out.append("```")
    out.append("")
    out.append(wrap(
        "LOAD CSV reads an empty field as null, and setting a property to null removes it, so "
        "`SET n += row` gives exactly the blank-cell behaviour the files assume. On versions before "
        "5.26 the dynamic label and type are not available: use "
        "`apoc.create.node([row[':LABEL']], props)` and "
        "`apoc.create.relationship(a, row[':TYPE'], props, b)`, or write one loader per label. The "
        "MATCH on the edge pass has no label, so it scans every node; that is fine for sixty-two "
        "nodes and wrong for a real graph, where you would index id per label first."))
    out.append("")
    out.append("### pandas and networkx")
    out.append("")
    out.append(wrap(
        "For the data science side, the same two files load into a directed multigraph in a dozen "
        "lines. A multigraph allows more than one edge between the same pair of nodes, which this "
        "model needs: a change can both form part of a master and amend one of its clauses."))
    out.append("")
    out.append("```python")
    out.append('''import pandas as pd
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
        print(n, attrs["label"], reaches_a_party(n))''')
    out.append("```")
    out.append("")
    out.append(wrap(
        "Run as it stands, that last loop prints True for every node except DOC-OF1, the "
        "superseded 2023 order form. That is a real gap in the sample rather than a bug in the "
        "walk: data.py gives party edges to the current order form only, and DOC-OF1's "
        "governed-by parent is shared terms on the vendor's paper, which carries no party edges "
        "of its own. It is recorded as a named exemption in the build and as a TODO in "
        "BUILD-REPORT.md."))
    out.append("")

    out.append("## Four worked queries")
    out.append("")
    out.append(wrap(
        "Each query below runs against the loaded sample and returns exactly the rows shown. They "
        "are ordered from the everyday question to the one that justifies the whole model."))
    out.append("")
    for i, query in enumerate(QUERIES, start=1):
        out.append("### %d. %s" % (i, query["title"]))
        out.append("")
        out.append(wrap(query["why"]))
        out.append("")
        out.append("```cypher")
        out.append(query["cypher"])
        out.append("```")
        out.append("")
        out.append("Expected result:")
        out.append("")
        header = query["expected"][0]
        out.append("| " + " | ".join(header) + " |")
        out.append("| " + " | ".join("---" for _ in header) + " |")
        for row in query["expected"][1:]:
            out.append("| " + " | ".join(cell if cell else "(null)" for cell in row) + " |")
        out.append("")
        out.append(wrap(query["note"]))
        out.append("")

    written.append(write_text("sample/README.md", "\n".join(out).rstrip() + "\n"))
    return written, node_header, edge_header, node_rows, edge_rows


# ---------------------------------------------------------------------------
# explainer.html
# ---------------------------------------------------------------------------

LAYERS = [
    ("L4", "Transaction", "l4", "Orders, responses, invoices and claims. What actually moved."),
    ("L3", "Content", "l3", "Clauses, classifications, term facts and obligations. What the paper says."),
    ("L2", "Agreement", "l2", "Instruments and the edges between them. The family trees."),
    ("L1", "Master data", "l1", "Entities, relationships, accounts, sites, products, people."),
    ("L0", "Reference", "l0", "Countries, currencies, incoterms, classifications, identifier schemes."),
]

CSS = """
:root {
  color-scheme: light dark;
  --bg: #f7f8f9;
  --surface: #ffffff;
  --surface-2: #eef0f3;
  --text: #191c21;
  --muted: #5a626e;
  --border: #d5d9df;
  --accent: #22345c;
  --accent-soft: #e7ecf4;
  --rule: #b9c0ca;
  --strata-4: #ffffff; --strata-3: #f8f9fb; --strata-2: #f1f3f6;
  --strata-1: #e8ebf0; --strata-0: #dee2e9;
  --nt-rel: #6d3f9c; --nt-master: #1a4f8a; --nt-part: #0f6355; --nt-comp: #7a5200;
  --nt-ch: #a03a1f;  --nt-wk: #145e75;    --nt-ord: #41620f;  --nt-sh: #6b4a2f;
  --nt-ev: #4a5568;  --nt-sec: #8f2245;
  --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, "Times New Roman", serif;
  --sans: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", "Courier New", monospace;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #171a1f;
    --surface: #1e222a;
    --surface-2: #252a33;
    --text: #e4e6ea;
    --muted: #a4acb9;
    --border: #343a45;
    --accent: #9db3d8;
    --accent-soft: #232c3d;
    --rule: #444c59;
    --strata-4: #1c2028; --strata-3: #21262f; --strata-2: #262c36;
    --strata-1: #2c333e; --strata-0: #333b47;
    --nt-rel: #c6a6ea; --nt-master: #8fb9e8; --nt-part: #5fc7b1; --nt-comp: #dcb45f;
    --nt-ch: #f0a58f;  --nt-wk: #83cbdd;    --nt-ord: #acd06e;  --nt-sh: #d0ad90;
    --nt-ev: #b6bfcc;  --nt-sec: #ef95af;
  }
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
  font-size: 17px;
  line-height: 1.6;
  -webkit-text-size-adjust: 100%;
}
.wrap { max-width: 62rem; margin: 0 auto; padding: 0 1.5rem; }
h1, h2, h3, h4 { font-family: var(--serif); font-weight: 600; line-height: 1.25; }
h1 { font-size: 2.4rem; margin: 0 0 0.4rem; letter-spacing: -0.01em; }
h2 { font-size: 1.75rem; margin: 2.6rem 0 0.8rem; }
h3 { font-size: 1.25rem; margin: 2rem 0 0.6rem; }
h4 { font-size: 1.05rem; margin: 1.4rem 0 0.4rem; }
p { margin: 0 0 1rem; max-width: 44rem; }
a { color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 2px; }
a:hover { text-decoration-thickness: 2px; }
:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; border-radius: 2px; }
code, kbd, samp { font-family: var(--mono); font-size: 0.86em; }
.lede { font-size: 1.15rem; color: var(--muted); max-width: 44rem; }
.skip {
  position: absolute; left: -9999px; top: 0; background: var(--surface);
  padding: 0.6rem 1rem; border: 2px solid var(--accent); z-index: 20;
}
.skip:focus { left: 1rem; top: 1rem; }

header.masthead { border-bottom: 1px solid var(--border); padding: 3rem 0 2rem; background: var(--surface); }
.version { font-family: var(--mono); font-size: 0.82rem; letter-spacing: 0.06em;
  color: var(--muted); margin-bottom: 0.6rem; }
.paths { display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1.5rem; padding: 0; list-style: none; }
.paths li { flex: 1 1 18rem; border-left: 3px solid var(--rule); padding: 0.2rem 0 0.2rem 0.9rem; }
.paths b { display: block; font-family: var(--serif); }
.paths span { color: var(--muted); font-size: 0.95rem; }

.invariant {
  margin: 2.5rem 0; padding: 1.4rem 1.6rem; background: var(--accent-soft);
  border: 1px solid var(--border); border-left: 5px solid var(--accent); border-radius: 3px;
}
.invariant .label {
  font-family: var(--mono); font-size: 0.75rem; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--accent); display: block; margin-bottom: 0.5rem;
}
.invariant p { margin: 0; max-width: 48rem; }
.invariant p + p { margin-top: 0.8rem; }

nav.strata { margin: 2.5rem 0 1rem; }
nav.strata ol { list-style: none; margin: 0; padding: 0; border: 1px solid var(--border);
  border-radius: 3px; overflow: hidden; }
nav.strata li { border-bottom: 1px solid var(--border); }
nav.strata li:last-child { border-bottom: 0; }
nav.strata a {
  display: grid; grid-template-columns: 4.5rem 1fr; gap: 1rem; align-items: baseline;
  padding: 0.85rem 1.1rem; text-decoration: none; color: inherit;
  border-left: 6px solid transparent; transition: background 120ms ease;
}
nav.strata .code { font-family: var(--mono); font-weight: 700; color: var(--accent); }
nav.strata .name { font-family: var(--serif); font-size: 1.1rem; }
nav.strata .desc { display: block; color: var(--muted); font-size: 0.92rem; }
nav.strata .l4 a { background: var(--strata-4); }
nav.strata .l3 a { background: var(--strata-3); }
nav.strata .l2 a { background: var(--strata-2); }
nav.strata .l1 a { background: var(--strata-1); }
nav.strata .l0 a { background: var(--strata-0); }
nav.strata a:hover, nav.strata a:focus-visible { background: var(--accent-soft); }
nav.strata a[aria-current="true"] { background: var(--accent-soft); border-left-color: var(--accent); }
.bedrock { font-size: 0.85rem; color: var(--muted); margin-top: 0.6rem; }

main section { padding-top: 1.5rem; border-top: 1px solid var(--border); margin-top: 3rem; }
main section:first-of-type { border-top: 0; }
.layer-tag {
  font-family: var(--mono); font-size: 0.75rem; letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--muted);
}
table { border-collapse: collapse; width: 100%; margin: 1.2rem 0; font-size: 0.94rem; }
th, td { text-align: left; padding: 0.55rem 0.7rem; border-bottom: 1px solid var(--border);
  vertical-align: top; }
th { font-family: var(--sans); font-weight: 600; font-size: 0.82rem; letter-spacing: 0.04em;
  text-transform: uppercase; color: var(--muted); border-bottom: 2px solid var(--rule); }
tbody tr:hover { background: var(--surface-2); }
.scroll { overflow-x: auto; }
table.kinds td:nth-child(1), table.kinds th:nth-child(1) { width: 8rem; }
table.kinds td:nth-child(2), table.kinds th:nth-child(2) { width: 40%; }
table.kinds td:nth-child(3), table.kinds th:nth-child(3) { width: 4rem; }
table.std td:nth-child(1), table.std th:nth-child(1) { width: 15%; }
table.std td:nth-child(2), table.std th:nth-child(2) { width: 15%; }
table.std td:nth-child(3), table.std th:nth-child(3) { width: 13%; }
table.entities td:nth-child(1), table.entities th:nth-child(1) { width: 9rem; }
table.entities td:nth-child(2), table.entities th:nth-child(2) { width: 9rem; }
td code { white-space: nowrap; }

ol.principles { counter-reset: p; list-style: none; padding: 0; margin: 1.2rem 0; }
ol.principles li { counter-increment: p; position: relative; padding-left: 2.6rem;
  margin-bottom: 1rem; max-width: 46rem; }
ol.principles li::before {
  content: counter(p); position: absolute; left: 0; top: 0.05rem;
  font-family: var(--mono); font-size: 0.8rem; font-weight: 700; color: var(--accent);
  border: 1px solid var(--rule); border-radius: 2px; width: 1.8rem; height: 1.8rem;
  display: grid; place-items: center;
}
ol.principles b { font-family: var(--serif); font-size: 1.05rem; display: block; }

.warn { border: 1px solid var(--rule); border-left: 5px solid var(--nt-ch); border-radius: 3px;
  padding: 1rem 1.2rem; margin: 1.4rem 0; background: var(--surface); }
.warn b { font-family: var(--serif); }
.warn p:last-child { margin-bottom: 0; }

.legend { display: flex; flex-wrap: wrap; gap: 0.5rem 1.4rem; padding: 0; margin: 1rem 0 1.6rem;
  list-style: none; }
.legend li { font-size: 0.92rem; display: flex; align-items: baseline; gap: 0.45rem; }
.swatch { width: 0.85rem; height: 0.85rem; border-radius: 2px; display: inline-block;
  flex: none; transform: translateY(1px); }
.legend .term { font-family: var(--mono); font-size: 0.85rem; }
.legend .gloss { color: var(--muted); }

details {
  border: 1px solid var(--border); border-radius: 3px; margin: 0.5rem 0; background: var(--surface);
}
details[open] { background: var(--surface); }
summary {
  cursor: pointer; padding: 0.7rem 1rem; font-family: var(--serif); font-size: 1.05rem;
  list-style-position: inside;
}
summary:hover { background: var(--surface-2); }
summary .fcode { font-family: var(--mono); font-size: 0.85rem; color: var(--accent);
  font-weight: 700; margin-right: 0.5rem; }
.details-body { padding: 0 1rem 1rem; border-top: 1px solid var(--border); }
.details-body > p:first-child { margin-top: 1rem; }
.dl-inline { margin: 0.6rem 0 0; font-size: 0.94rem; }
.dl-inline dt { font-weight: 600; color: var(--muted); font-size: 0.82rem;
  letter-spacing: 0.04em; text-transform: uppercase; margin-top: 0.7rem; }
.dl-inline dd { margin: 0.15rem 0 0; }
.dl-inline dd + dd { margin-top: 0.5rem; }

pre.tree {
  font-family: var(--mono); font-size: 0.82rem; line-height: 1.65; overflow-x: auto;
  background: var(--surface-2); border: 1px solid var(--border); border-radius: 3px;
  padding: 0.9rem 1rem; margin: 1rem 0 0; white-space: pre;
}
pre.tree .tc { color: var(--rule); }
pre.tree .ek { color: var(--muted); }
pre.tree .ek-l { font-style: italic; }
pre.tree .ek-t { letter-spacing: 0.02em; }
pre.tree .ek-e { text-decoration: underline dotted; text-underline-offset: 2px; }
pre.tree .nd { font-weight: 600; }
pre.tree .ntag { font-weight: 400; opacity: 0.75; }
pre.tree .pr { color: var(--muted); }
pre.tree .xr { color: var(--nt-ch); font-style: italic; }
.nt-rel { color: var(--nt-rel); } .nt-master { color: var(--nt-master); }
.nt-part { color: var(--nt-part); } .nt-comp { color: var(--nt-comp); }
.nt-ch { color: var(--nt-ch); } .nt-wk { color: var(--nt-wk); }
.nt-ord { color: var(--nt-ord); } .nt-sh { color: var(--nt-sh); }
.nt-ev { color: var(--nt-ev); } .nt-sec { color: var(--nt-sec); }
.sw-rel { background: var(--nt-rel); } .sw-master { background: var(--nt-master); }
.sw-part { background: var(--nt-part); } .sw-comp { background: var(--nt-comp); }
.sw-ch { background: var(--nt-ch); } .sw-wk { background: var(--nt-wk); }
.sw-ord { background: var(--nt-ord); } .sw-sh { background: var(--nt-sh); }
.sw-ev { background: var(--nt-ev); } .sw-sec { background: var(--nt-sec); }

.cat-head { margin-top: 2rem; }
.controls { display: flex; gap: 0.6rem; margin: 1rem 0; flex-wrap: wrap; }
.controls button {
  font: inherit; font-size: 0.88rem; padding: 0.35rem 0.8rem; cursor: pointer;
  background: var(--surface); color: var(--text); border: 1px solid var(--rule); border-radius: 3px;
}
.controls button:hover { background: var(--surface-2); }

.callout { border: 1px solid var(--border); border-radius: 3px; padding: 1.2rem 1.4rem;
  background: var(--surface); margin: 1.2rem 0; }
.callout h3 { margin-top: 0; }
.xcat { list-style: none; padding: 0; margin: 0; }
.xcat li { padding: 0.8rem 0; border-bottom: 1px dashed var(--rule); max-width: 48rem; }
.xcat li:last-child { border-bottom: 0; padding-bottom: 0; }
.xcat b { font-family: var(--serif); font-size: 1.05rem; }
.xcat .edges { font-family: var(--mono); font-size: 0.8rem; color: var(--accent); }

ol.process { max-width: 46rem; padding-left: 1.4rem; }
ol.process li { margin-bottom: 0.6rem; }

.repo { font-family: var(--mono); font-size: 0.88rem; }
.repo td:first-child { white-space: nowrap; color: var(--accent); }

footer { border-top: 1px solid var(--border); margin-top: 3.5rem; padding: 2rem 0 3rem;
  color: var(--muted); font-size: 0.92rem; background: var(--surface); }
footer p { max-width: 48rem; }
.status-note { color: var(--muted); font-size: 0.88rem; margin: 0.2rem 0 1rem; }
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important; }
}
@media (max-width: 40rem) {
  body { font-size: 16px; }
  h1 { font-size: 1.9rem; }
  nav.strata a { grid-template-columns: 1fr; gap: 0.15rem; }
}
"""

JS = """
(function () {
  var main = document.getElementById('content');
  if (!main) return;

  var bar = document.createElement('div');
  bar.className = 'controls';
  [['Expand all', true], ['Collapse all', false]].forEach(function (pair) {
    var b = document.createElement('button');
    b.type = 'button';
    b.textContent = pair[0];
    b.addEventListener('click', function () {
      var blocks = document.querySelectorAll('#layer-l2 details');
      for (var i = 0; i < blocks.length; i++) { blocks[i].open = pair[1]; }
    });
    bar.appendChild(b);
  });
  var anchor = document.getElementById('families-controls');
  if (anchor) { anchor.appendChild(bar); }

  var links = {};
  var navLinks = document.querySelectorAll('nav.strata a');
  for (var i = 0; i < navLinks.length; i++) {
    links[navLinks[i].getAttribute('href').slice(1)] = navLinks[i];
  }
  if (!('IntersectionObserver' in window)) return;
  var current = null;
  var io = new IntersectionObserver(function (entries) {
    for (var i = 0; i < entries.length; i++) {
      if (!entries[i].isIntersecting) continue;
      var id = entries[i].target.id;
      if (!links[id] || current === id) continue;
      if (current && links[current]) { links[current].removeAttribute('aria-current'); }
      links[id].setAttribute('aria-current', 'true');
      current = id;
    }
  }, { rootMargin: '-20% 0px -70% 0px' });
  var sections = document.querySelectorAll('main section[id]');
  for (var j = 0; j < sections.length; j++) { io.observe(sections[j]); }
})();
"""


def h_table(headers, rows, classes=""):
    out = ['<div class="scroll"><table%s>' % ((' class="%s"' % classes) if classes else "")]
    out.append("<thead><tr>" + "".join("<th scope=\"col\">%s</th>" % esc(h) for h in headers)
               + "</tr></thead><tbody>")
    for row in rows:
        cells = "".join("<td>%s</td>" % cell for cell in row)
        out.append("<tr>%s</tr>" % cells)
    out.append("</tbody></table></div>")
    return "\n".join(out)


def family_details(family):
    return """<details id="fam-%s">
<summary><span class="fcode">%s</span>%s</summary>
<div class="details-body">
<p>%s</p>
%s
<dl class="dl-inline">
<dt>Properties</dt><dd>%s</dd>
<dt>Complexity</dt><dd>%s</dd>
</dl>
</div>
</details>""" % (
        esc(family["code"]).lower(),
        esc(family["code"] + "."),
        esc(family["name"]),
        esc(" ".join(family["test"].split())),
        render_tree_html(family["tree"]),
        esc(" ".join(family["props"].split())),
        "</dd><dd>".join(esc(" ".join(item.split())) for item in family["complexity"]),
    )


def overlay_details(overlay):
    return """<details id="ov-%s">
<summary><span class="fcode">%s</span>%s</summary>
<div class="details-body">
<p>%s</p>
<dl class="dl-inline">
<dt>Node examples</dt><dd>%s</dd>
<dt>Key edges</dt><dd>%s</dd>
</dl>
</div>
</details>""" % (
        esc(overlay["code"]).lower(),
        esc(overlay["code"] + "."),
        esc(overlay["name"]),
        esc(" ".join(overlay["desc"].split())),
        esc(overlay["nodes"]),
        esc(overlay["edges"]),
    )


def build_explainer():
    parts = []
    parts.append("<!DOCTYPE html>")
    parts.append('<html lang="en-GB">')
    parts.append("<head>")
    parts.append('<meta charset="utf-8">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    parts.append("<title>Distributor Contract Graph v%s</title>" % esc(data.VERSION))
    parts.append('<meta name="description" content="The Distributor Contract Graph: a layered '
                 'model for contract knowledge graphs in B2B distribution.">')
    parts.append("<style>%s</style>" % CSS)
    parts.append("</head>")
    parts.append("<body>")
    parts.append('<a class="skip" href="#content">Skip to content</a>')

    # ---- masthead --------------------------------------------------------
    parts.append('<header class="masthead"><div class="wrap">')
    parts.append('<p class="version">Open standard, DCG v%s</p>' % esc(data.VERSION))
    parts.append("<h1>Distributor Contract Graph</h1>")
    parts.append('<p class="lede">A layered model for contract knowledge graphs in B2B '
                 'distribution: five layers, a nine-type master data spine, thirty-six contract '
                 'families and six overlays, held together by one invariant that survives even '
                 'when everything else about a document is unknown.</p>')
    parts.append('<ul class="paths">')
    parts.append('<li><b>Legal</b><span>Start at the invariant, then the families.</span></li>')
    parts.append('<li><b>Data science</b><span>Start at the spine, then the registries and the '
                 'sample graph.</span></li>')
    parts.append("</ul>")
    parts.append("</div></header>")

    parts.append('<div class="wrap">')

    # ---- invariant -------------------------------------------------------
    parts.append('<div class="invariant" role="note" aria-labelledby="inv-label">')
    parts.append('<span class="label" id="inv-label">The survival invariant</span>')
    parts.append("<p>%s</p>" % esc(INVARIANT_TEXT))
    parts.append("</div>")

    # ---- strata navigation ----------------------------------------------
    parts.append('<nav class="strata" aria-label="The five layers">')
    parts.append('<h2 id="layers-heading">The five layers</h2>')
    parts.append('<p>Read the stack from the bottom up. Master data is the bedrock: everything '
                 'above it resolves down to an entity, an account or a product, and a layer that '
                 'cannot resolve downwards is not yet part of the graph.</p>')
    parts.append("<ol>")
    for code, name, anchor, desc in LAYERS:
        parts.append('<li class="%s"><a href="#layer-%s"><span class="code">%s</span>'
                     '<span><span class="name">%s</span>'
                     '<span class="desc">%s</span></span></a></li>'
                     % (anchor, anchor, esc(code), esc(name), esc(desc)))
    parts.append("</ol>")
    parts.append('<p class="bedrock">L4 sits on L3, on L2, on L1, on L0. The relationship node '
                 'straddles the L1 and L2 boundary: anchored in master data, used by the agreement '
                 'layer.</p>')
    parts.append("</nav>")

    parts.append('<main id="content">')

    # ---- L0 --------------------------------------------------------------
    ref_types = [n for n in data.NODE_TYPES if n[2].startswith("0")]
    parts.append('<section id="layer-l0" aria-labelledby="h-l0">')
    parts.append('<p class="layer-tag">Layer 0</p>')
    parts.append('<h2 id="h-l0">Reference</h2>')
    parts.append("<p>Closed lists that everything else points at. Nothing here is negotiated and "
                 "nothing here belongs to a counterparty. Reference data is boring on purpose: it "
                 "is the layer that lets two systems agree on what Germany means.</p>")
    parts.append(h_table(
        ["Node type", "Definition", "Examples", "Standard"],
        [["<code>%s</code>" % esc(n[0]), esc(n[3]), "<code>%s</code>" % esc(n[4]),
          esc({"country": "ISO 3166", "currency": "ISO 4217", "incoterm": "ICC Incoterms 2020",
               "classification_code": "UNSPSC or ETIM",
               "identifier_scheme": "ISO 6523 and others"}.get(n[0], ""))]
         for n in ref_types]))

    # ---- L1 --------------------------------------------------------------
    spine = {n[0]: n for n in data.NODE_TYPES}
    parts.append("</section>")
    parts.append('<section id="layer-l1" aria-labelledby="h-l1">')
    parts.append('<p class="layer-tag">Layer 1</p>')
    parts.append('<h2 id="h-l1">Master data</h2>')
    parts.append("<p>The spine. Nine entity types and eight principles, and every one of the "
                 "principles exists because getting it wrong has a known cost. Category (customer, "
                 "supplier, vendor) is a property of the relationship, never of the legal entity: "
                 "one real-world party can hold all three at once through three relationship "
                 "nodes.</p>")
    parts.append("<h3>The eight principles</h3>")
    parts.append('<ol class="principles">')
    for title, body in PRINCIPLES:
        parts.append("<li><b>%s</b>%s</li>" % (esc(title), esc(body)))
    parts.append("</ol>")
    parts.append("<h3>The nine entity types</h3>")
    parts.append(h_table(
        ["Type", "Name", "Definition", "Examples"],
        [["<code>%s</code>" % esc(i), esc(spine[i][1]), esc(spine[i][3]),
          "<code>%s</code>" % esc(spine[i][4])] for i in SPINE_IDS],
        classes="entities"))
    parts.append('<div class="warn">')
    parts.append("<p><b>Ownership is not grouping.</b> Legal ownership travels along "
                 "<code>owns</code> edges between legal entities: who controls whom, whose balance "
                 "sheet consolidates, who can bind a subsidiary. Commercial grouping travels along "
                 "<code>member_of</code> edges into a group node: a buying group, a franchise "
                 "network, a global account programme.</p>")
    parts.append("<p>Conflating the two produces the two classic errors in opposite directions: "
                 "granting a buying group member the parent company's negotiated terms, and "
                 "refusing a genuine subsidiary the terms its parent signed for it. Keep them as "
                 "two hierarchies and both questions stay answerable.</p>")
    parts.append("</div>")

    # ---- L2 --------------------------------------------------------------
    parts.append("</section>")
    parts.append('<section id="layer-l2" aria-labelledby="h-l2">')
    parts.append('<p class="layer-tag">Layer 2</p>')
    parts.append('<h2 id="h-l2">Agreement</h2>')
    parts.append("<p>Instruments and the edges between them. One node per legal instrument that "
                 "can change independently. Executed instruments are nodes, and so are instruments "
                 "binding by notice (status: notified); drafts are not. The file is a property of "
                 "the instrument, not a node in its own right. Every node has exactly one "
                 "structural parent, and edges are directed with the dependent pointing at what it "
                 "depends on.</p>")
    parts.append("<p>Structural edges build the tree. Lifecycle edges change nodes over time. "
                 "Reference edges cut across branches, and they are the reason this is a graph "
                 "rather than a folder structure.</p>")

    parts.append("<h3>Node types in the trees</h3>")
    parts.append('<ul class="legend">')
    for key, name in data.NODE_TYPE_NAMES.items():
        parts.append('<li><span class="swatch sw-%s"></span><span class="term nt-%s">%s</span>'
                     '<span class="gloss">%s</span></li>' % (key, key, esc(key), esc(name)))
    parts.append("</ul>")

    parts.append("<h3>Edge kinds</h3>")
    kind_gloss = {
        "structural": "Builds the tree. Child points at parent, one structural parent per node.",
        "lifecycle": "Changes a node over time: amends, supersedes, varies, extends, terminates.",
        "reference": "Cuts across branches and across categories. The reason the graph exists.",
        "party": "Points an instrument at a signatory legal entity. Half one of the invariant.",
        "transaction": "Points a transaction at an account or at what it answers. Half two.",
        "masterdata": "Points the agreement layer down into the spine: territories, sites, "
                      "products, org units.",
        "content": "Points a document at its clauses, and clauses at facts and obligations.",
        "evidence": "Points a non-contractual record at what it evidences, with a validity window.",
    }
    kind_counts = {}
    for row in data.EDGE_TYPES:
        kind_counts[row[2]] = kind_counts.get(row[2], 0) + 1
    kind_examples = {}
    for row in data.EDGE_TYPES:
        kind_examples.setdefault(row[2], []).append(row[0])
    parts.append(h_table(
        ["Kind", "What it does", "Count", "Examples"],
        [[esc(kind), esc(kind_gloss.get(kind, "")), str(kind_counts[kind]),
          "<code>%s</code>" % esc(", ".join(kind_examples[kind][:4]))]
         for kind in ["structural", "lifecycle", "reference", "party", "transaction",
                      "masterdata", "content", "evidence"]],
        classes="kinds"))
    parts.append("<p>Sixty edge types in all, listed in full with direction rules and time "
                 "properties in <code>registries/edge_types.csv</code>.</p>")

    parts.append("<h3>The thirty-six families</h3>")
    parts.append("<p>Family membership is decided by structure, never by the title on the cover. "
                 "The title is recorded as an alias and used as a hint, never as a decision. Five "
                 "classifying properties on master-level nodes carry the tests: scope, paper, "
                 "commercial completeness, commitment and appointment.</p>")
    parts.append('<div id="families-controls"></div>')
    for category, _filename, _prefix in CATEGORIES:
        families = [f for f in data.FAMILIES if f["cat"] == category]
        parts.append('<h4 class="cat-head">%s (%d families)</h4>' % (esc(category), len(families)))
        for family in families:
            parts.append(family_details(family))

    parts.append("<h3>The six overlays</h3>")
    parts.append("<p>An overlay is not a family. It is a set of node types and edges that can "
                 "appear under any family tree in any category: a guarantee secures obligations "
                 "wherever they arise, a data processing agreement forms part of whatever master "
                 "it was signed under.</p>")
    for overlay in data.OVERLAYS:
        parts.append(overlay_details(overlay))

    # ---- L3 --------------------------------------------------------------
    parts.append("</section>")
    parts.append('<section id="layer-l3" aria-labelledby="h-l3">')
    parts.append('<p class="layer-tag">Layer 3</p>')
    parts.append('<h2 id="h-l3">Content</h2>')
    parts.append("<p>What the paper actually says, in four sub-layers. Each one is optional: a "
                 "document with no content layer at all is still a working node, which is the "
                 "point of the degradation ladder.</p>")
    parts.append(h_table(
        ["Sub-layer", "What it holds"],
        [[esc(name), esc(body)] for name, body in SUB_LAYERS]))

    parts.append("<h3>The standards stack</h3>")
    parts.append("<p>Nineteen slots, grouped by what we do with them. The dropped rows are here on "
                 "purpose: a standard that names what it rejected, and why, is easier to trust "
                 "than one that lists only what it likes.</p>")
    by_status = {}
    for row in data.STANDARDS:
        by_status.setdefault(row[3], []).append(row)
    for status_key, status_name in STATUS_LABELS:
        rows = by_status.get(status_key, [])
        if not rows:
            continue
        parts.append("<h4>%s</h4>" % esc(status_name))
        parts.append('<p class="status-note">%s</p>' % esc(STATUS_NOTES[status_key]))
        parts.append(h_table(
            ["Slot", "Standard", "Steward", "What we take", "Adoption evidence"],
            [[esc(r[0]),
              '<a href="%s">%s</a>' % (esc(r[6]), esc(r[1])),
              esc(r[2]), esc(r[4]), esc(r[5])] for r in rows],
            classes="std"))

    # ---- L4 --------------------------------------------------------------
    parts.append("</section>")
    parts.append('<section id="layer-l4" aria-labelledby="h-l4">')
    parts.append('<p class="layer-tag">Layer 4</p>')
    parts.append('<h2 id="h-l4">Transaction</h2>')
    parts.append("<p>Orders, order responses, invoices and claims. This layer is already "
                 "standardised and we do not reinvent it: UBL (ISO/IEC 19845) gives the order, "
                 "order response, despatch advice and invoice shapes, and its "
                 "<code>DocumentReference</code> element is where the placed-under link lives when "
                 "the transaction travels between systems.</p>")
    parts.append("<p>Inside the graph, <code>placed_under</code> attaches a transaction to the "
                 "lowest node that actually governs it, not to the top of the tree. A purchase "
                 "order under a local participation points at the participation, not at the global "
                 "master; the walk up to the master is a query, not a stored edge. Alongside it, "
                 "<code>ordered_by</code> points at the account, which is the second half of the "
                 "invariant and the reason a transaction can always be attributed even when the "
                 "paperwork above it is a mess.</p>")
    parts.append(h_table(
        ["Node type", "Definition", "Examples"],
        [["<code>%s</code>" % esc(n[0]), esc(n[3]), "<code>%s</code>" % esc(n[4])]
         for n in data.NODE_TYPES if n[2].startswith("4")]))

    # ---- cross-category --------------------------------------------------
    parts.append("</section>")
    parts.append('<section id="cross-category" aria-labelledby="h-xcat">')
    parts.append('<h2 id="h-xcat">Edges that cross categories</h2>')
    parts.append("<p>The customer, supplier and vendor sides are usually run by different teams "
                 "with different systems. These four edges are where the money and the risk "
                 "actually sit, and every one of them is invisible in a folder structure.</p>")
    parts.append('<div class="callout"><ul class="xcat">')
    for title, edges, body in CROSS_CATEGORY_CALLOUTS:
        parts.append('<li><b>%s</b> <span class="edges">%s</span><br>%s</li>'
                     % (esc(title), esc(edges), esc(body)))
    parts.append("</ul></div>")

    # ---- catch-all -------------------------------------------------------
    parts.append("</section>")
    parts.append('<section id="catch-all" aria-labelledby="h-catch">')
    parts.append('<h2 id="h-catch">When nothing fits</h2>')
    parts.append("<p>Every category carries an X0 unclassified family: C0, S0 and V0 in "
                 "<code>registries/families.csv</code>. A document that cannot be placed is never "
                 "left out of the graph, because a document outside the graph is a document nobody "
                 "will find again.</p>")
    parts.append('<ol class="process">')
    for step in CATCH_ALL_PROCESS:
        parts.append("<li>%s</li>" % esc(step))
    parts.append("</ol>")

    # ---- repo map --------------------------------------------------------
    parts.append("</section>")
    parts.append('<section id="repo" aria-labelledby="h-repo">')
    parts.append('<h2 id="h-repo">The repository</h2>')
    parts.append(h_table(["Path", "What it is"],
                         [["<code>%s</code>" % esc(p), esc(d)] for p, d in REPO_MAP],
                         classes="repo"))
    parts.append("<p>Everything derived from <code>build/data.py</code> is generated. Regenerate "
                 "the whole package, this page included, with "
                 "<code>python3 build/build.py</code> from the repository root; the build fails on "
                 "any validation error and prints the counts it asserted.</p>")
    parts.append("</section>")

    parts.append("</main>")
    parts.append("</div>")

    parts.append('<footer><div class="wrap">')
    parts.append("<p><strong>Distributor Contract Graph v%s.</strong> Versioned with semantic "
                 "versioning. Proposed licence: CC BY 4.0 for the text and the registries, "
                 "marked as a proposal to confirm before release.</p>" % esc(data.VERSION))
    parts.append("<p>A practitioner-built open standard. It was written by people who have had to "
                 "answer these questions against real filing systems, and it is published so that "
                 "the next team does not have to derive it again. Corrections and family proposals "
                 "are more useful than agreement.</p>")
    parts.append("</div></footer>")
    parts.append("<script>%s</script>" % JS)
    parts.append("</body>")
    parts.append("</html>")

    return write_text("explainer.html", "\n".join(parts))


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------

def camel_to_snake(label):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", label).lower()


def validate(node_rows, edge_rows, alias_rows, family_rows):
    errors = []
    warnings = []

    node_ids = {row[0] for row in data.SAMPLE_NODES}
    node_label = {row[0]: row[2] for row in data.SAMPLE_NODES}
    node_type_ids = {row[0] for row in data.NODE_TYPES}
    edge_type_ids = {row[0] for row in data.EDGE_TYPES}

    say("Validation")
    say("=" * 72)

    # 1. edge endpoints exist
    dangling = []
    for start, edge_type, end, _props in data.SAMPLE_EDGES:
        if start not in node_ids:
            dangling.append("%s -[%s]-> %s: start id not in nodes.csv" % (start, edge_type, end))
        if end not in node_ids:
            dangling.append("%s -[%s]-> %s: end id not in nodes.csv" % (start, edge_type, end))
    errors.extend(dangling)
    say("1. Sample edge endpoints resolve            %s (%d edges, %d endpoints checked)"
        % ("PASS" if not dangling else "FAIL", len(data.SAMPLE_EDGES), 2 * len(data.SAMPLE_EDGES)))

    # 2. labels map to node type ids
    bad_labels = []
    labels = sorted({row[2] for row in data.SAMPLE_NODES})
    for label in labels:
        if camel_to_snake(label) not in node_type_ids:
            bad_labels.append("label %s maps to %s, which is not a node_types id"
                              % (label, camel_to_snake(label)))
    errors.extend(bad_labels)
    say("2. Node labels map to the node registry     %s (%d distinct labels)"
        % ("PASS" if not bad_labels else "FAIL", len(labels)))

    # 3. edge types match the registry
    bad_types = []
    types_used = sorted({row[1] for row in data.SAMPLE_EDGES})
    for edge_type in types_used:
        if edge_type.lower() not in edge_type_ids:
            bad_types.append("edge type %s lowercases to %s, which is not an edge_types id"
                             % (edge_type, edge_type.lower()))
    errors.extend(bad_types)
    say("3. Edge types match the edge registry       %s (%d distinct types)"
        % ("PASS" if not bad_types else "FAIL", len(types_used)))

    # 4. family codes unique, alias hints resolve
    codes = [row[0] for row in family_rows]
    duplicates = sorted({c for c in codes if codes.count(c) > 1})
    if duplicates:
        errors.append("duplicate family codes: %s" % ", ".join(duplicates))
    known = set(codes) | {o["code"] for o in data.OVERLAYS}
    bad_hints = sorted({row[2] for row in alias_rows if row[2] and row[2] not in known})
    for hint in bad_hints:
        errors.append("alias family_hint %s does not exist in families or overlays" % hint)
    blank_hints = sum(1 for row in alias_rows if not row[2])
    say("4. Family codes unique, alias hints resolve %s (%d codes, %d aliases, %d family-neutral)"
        % ("PASS" if not duplicates and not bad_hints else "FAIL",
           len(codes), len(alias_rows), blank_hints))

    # 5. the invariant on the sample
    outgoing = {}
    for start, edge_type, end, _props in data.SAMPLE_EDGES:
        outgoing.setdefault(start, []).append((edge_type, end))

    def walk(node_id, seen):
        """Return 'direct', an inheritance path, or None."""
        if node_id in seen:
            return None
        seen.add(node_id)
        edges = outgoing.get(node_id, [])
        if any(edge_type == "PARTY_TO" for edge_type, _end in edges):
            return "direct"
        for edge_type, end in edges:
            if edge_type in INHERITING_EDGES:
                found = walk(end, seen)
                if found:
                    step = "%s -> %s" % (edge_type.lower(), end)
                    return step if found == "direct" else "%s, %s" % (step, found)
        return None

    direct, inherited, unsatisfied = [], [], []
    for node_id, name, label, _layer, _props in data.SAMPLE_NODES:
        if label not in ("Master", "Participation", "WorkInstrument"):
            continue
        result = walk(node_id, set())
        if result == "direct":
            direct.append((node_id, label))
        elif result:
            inherited.append((node_id, label, result))
        else:
            unsatisfied.append((node_id, label, name))

    orders_missing = []
    order_count = 0
    for node_id, _name, label, _layer, _props in data.SAMPLE_NODES:
        if label != "Order":
            continue
        order_count += 1
        if not any(edge_type == "ORDERED_BY" for edge_type, _end in outgoing.get(node_id, [])):
            orders_missing.append(node_id)

    exempt = [row for row in unsatisfied if row[0] in INVARIANT_EXEMPTIONS]
    real_failures = [row for row in unsatisfied if row[0] not in INVARIANT_EXEMPTIONS]
    for node_id, label, name in real_failures:
        errors.append("invariant: %s (%s, %s) reaches no party_to edge, directly or by inheritance"
                      % (node_id, label, name))
    for node_id in orders_missing:
        errors.append("invariant: order %s has no ordered_by edge" % node_id)
    for node_id, label, _name in exempt:
        warnings.append("invariant exemption: %s (%s). %s"
                        % (node_id, label, INVARIANT_EXEMPTIONS[node_id]))

    say("5. Survival invariant on the sample         %s (%d direct, %d inherited, %d exempt, "
        "%d failing; %d/%d orders have ordered_by)"
        % ("PASS" if not real_failures and not orders_missing else "FAIL",
           len(direct), len(inherited), len(exempt), len(real_failures),
           order_count - len(orders_missing), order_count))
    say("")
    say("   Party edges, node by node")
    for node_id, label in direct:
        say("     direct      %-14s %s" % (node_id, label))
    for node_id, label, path in inherited:
        say("     inherited   %-14s %s via %s" % (node_id, label, path))
    for node_id, label, _name in exempt:
        say("     exempt      %-14s %s" % (node_id, label))
    say("   %s" % INVARIANT_SHARED_TERMS_NOTE)
    say("")

    # 6. counts
    counts = {
        "families": len(data.FAMILIES),
        "overlays": len(data.OVERLAYS),
        "node_types": len(data.NODE_TYPES),
        "edge_types": len(data.EDGE_TYPES),
        "aliases": len(alias_rows),
        "properties": len(data.PROPERTIES),
        "standards": len(data.STANDARDS),
        "sample_nodes": len(node_rows),
        "sample_edges": len(edge_rows),
    }
    say("6. Counts")
    for key in EXPECTED:
        actual, expected = counts[key], EXPECTED[key]
        ok = "ok" if actual == expected else "MISMATCH"
        say("     %-14s %4d  expected %4d  %s" % (key, actual, expected, ok))
        if actual != expected:
            errors.append("count mismatch: %s is %d, expected %d" % (key, actual, expected))
    say("     %-14s %4d  (36 families plus the C0, S0 and V0 catch-all rows)"
        % ("families.csv", len(family_rows)))
    say("")
    return errors, warnings, counts


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    say("Distributor Contract Graph v%s, build" % data.VERSION)
    say("Repository root: %s" % ROOT)
    say("")

    family_files = build_family_files()
    registry_files, alias_rows, family_rows = build_registries()
    sample_files, node_header, edge_header, node_rows, edge_rows = build_sample()
    explainer = build_explainer()

    written = family_files + registry_files + sample_files + [explainer]
    say("Files written")
    for path in written:
        say("     %-34s %7d bytes" % (path.relative_to(ROOT), path.stat().st_size))
    say("")
    say("Sample node columns: %s" % ", ".join(node_header))
    say("Sample edge columns: %s" % ", ".join(edge_header))
    say("")

    errors, warnings, _counts = validate(node_rows, edge_rows, alias_rows, family_rows)

    details_count = explainer.read_text(encoding="utf-8").count("<details")
    expected_details = len(data.FAMILIES) + len(data.OVERLAYS)
    say("7. explainer.html details blocks            %s (%d, expected %d)"
        % ("PASS" if details_count == expected_details else "FAIL",
           details_count, expected_details))
    if details_count != expected_details:
        errors.append("explainer.html has %d details blocks, expected %d"
                      % (details_count, expected_details))

    # written as an escape, not as the character itself, so that a repository-wide
    # grep for the em dash returns nothing at all
    em_dash = "\u2014"
    scanned = list(written)
    for extra in ("README.md", "BUILD-REPORT.md", "build/build.py", "build/data.py"):
        candidate = ROOT / extra
        if candidate.exists():
            scanned.append(candidate)
    em_dash_hits = [str(path.relative_to(ROOT)) for path in scanned
                    if em_dash in path.read_text(encoding="utf-8")]
    if em_dash_hits:
        errors.append("em dash found in: %s" % ", ".join(em_dash_hits))
    say("8. No em dashes anywhere in the repository  %s (%d files scanned)"
        % ("PASS" if not em_dash_hits else "FAIL", len(scanned)))
    say("")

    if warnings:
        say("Warnings (%d)" % len(warnings))
        for warning in warnings:
            say("     %s" % warning)
        say("")

    if errors:
        say("BUILD FAILED: %d error(s)" % len(errors))
        for error in errors:
            say("     %s" % error)
        return 1

    say("Validation passed. %d files written, %d warning(s)." % (len(written), len(warnings)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

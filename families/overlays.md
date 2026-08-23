# Overlays

Six overlays cut across the families. An overlay is not a family: it is a set of node types and
edges that can appear under any family tree, in any category. A guarantee secures obligations
wherever they arise; a data processing agreement forms part of whatever master it was signed
under.

## O1. Security

Instruments that secure obligations arising anywhere in the graph. Guarantees (parent, bank,
personal), promissory notes and post-dated cheques (Middle East practice), letters of credit by
type (sight, usance, standby, confirmed), bonds (performance, advance payment, retention),
charges. Each has its own lifecycle (expiry, release, calls) and party edges into master data,
because the guarantor is rarely the account holder.

Node examples
: Guarantee; Promissory Note; Post-Dated Cheque; Letter of Credit; Bond; Charge; Debenture

Key edges
: secures -> obligations or agreements in any family; party edges -> guarantor legal entity in master data

## O2. Dispute resolution

Standstill agreements, settlement agreements, Tomlin and consent orders, waiver letters. Rare,
but their extinguishes edges point at obligations elsewhere in the graph, which makes them
disproportionately valuable to model.

Node examples
: Standstill Agreement; Settlement Agreement; Tomlin Order; Consent Order; Waiver Letter

Key edges
: extinguishes -> obligations or claims anywhere in the graph; varies -> surviving terms

## O3. Pre-contract

NDAs, LOIs and heads of terms, bids and tender submissions, teaming agreements. Carries the
superseded-by-master property, because whether the master supersedes the NDA is a question every
family inherits. oneNDA is the canonical standard-form node here.

Node examples
: NDA (oneNDA canonical); CDA; LOI; Heads of Terms; MOU; Bid; Tender Submission; Teaming Agreement

Key edges
: superseded by -> master (property: yes or no); incorporated into -> master

## O4. Codes and policies

Customer-imposed supplier codes of conduct pointing at us, and our codes imposed on suppliers.
Sometimes made contractual, often standalone; the contractual flag is the property that matters.

Node examples
: Supplier Code of Conduct (theirs -> us); Code of Conduct (ours -> suppliers); ESG Policy; Anti-Bribery Policy

Key edges
: incorporates or references from any family master; contractual: yes or no

## O5. Trading channels

EDI, API and PunchOut. Usually a schedule inside another family because an underlying contract
is typically negotiated; occasionally a standalone trading partner agreement. E-commerce
accounts are a family (C12), not this overlay. Agent-based ordering is a reserved future channel
type.

Node examples
: EDI Schedule; API Schedule; PunchOut Schedule; Trading Partner Agreement; cXML Agreement

Key edges
: forms part of -> governing family master; enables -> transaction layer channel property

## O6. Data protection

DPAs, SCCs or IDTA, joint controller terms, transfer assessments. The same node types appear in
every category with the distributor's role flipping between controller and processor. Facts are
typed like any other terms; DPA here means data processing, disambiguated from the S9 sense by
category.

Node examples
: DPA (data processing sense); SCCs; IDTA; Joint Controller Terms; Transfer Risk Assessment

Key edges
: forms part of -> any family master; role property: controller, processor, joint

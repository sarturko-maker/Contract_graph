# Supplier families

12 families on the supplier side. Each entry gives the family test, the tree, the terminology
that turns up on real cover pages, the classifying properties and the complexity that makes the
family worth separating.

## S1. Authorised distribution and channel programmes

Appointment is yes: the agreement confers channel status and generates programme children such
as price protection, stock rotation, ship-and-debit and SPA eligibility, often through annual
programme terms that re-issue each year and instruments that bind by notice rather than
signature. The absence of those children is what sends a document to S2 instead.

```
Relationship: VendorCo [relationship]
└── Distribution agreement 2018 [master-level] {appointment: yes}
    ├── (forms part of) Territory schedule [component]
    ├── (forms part of) Product schedule [component] {updated by notice}
    ├── (forms part of) Price list [component] ~> supersedes by notice
    ├── (forms part of) Programme terms 2026 [component] ~> supersedes 2025
    │   └── (forms part of) Price protection, stock rotation, S&D terms [component]
    ├── (incorporates) End-user terms [shared / by reference] ~> flows down to C10
    ├── (amends) Amendment 1 [change]
    └── (placed under) Our POs to vendor [order / transaction]
```

### Terminology

Master
: Distribution Agreement; Authorised Distributor Agreement; Master Distributor Agreement; Channel Partner Agreement; Dealer Agreement (their paper); Franchised Distributor Agreement

Programme
: Programme Terms; Partner Programme Guide; Channel Programme Terms; Price Protection Terms; Stock Rotation Policy; Ship-and-Debit Terms; POS Reporting Requirements

### Properties

appointment: yes | update mechanism: by notice for lists, signature for the master | node
status: notified where bound by notice

### Complexity

- Instruments that bind by notice are still nodes, with status notified rather than signed.
- Annual programme terms re-issue wholesale; the supersedes chain carries the years.
- End-user terms flow down into C10, the family's signature cross-category edge.

## S2. Master supply or purchase, no appointment

Buy-side relationship terms without channel status. Structurally a mirror of C2. The defining
feature is the absence of programme children: no price protection, no stock rotation, no ship-
and-debit eligibility.

```
Relationship: MakerCo [relationship]
└── Master purchase agreement [master-level] {appointment: no}
    ├── (forms part of) Pricing exhibit [component]
    ├── (forms part of) Quality and delivery terms [component]
    └── (placed under) Our POs [order / transaction]
```

### Terminology

Master
: Master Purchase Agreement; Master Supply Agreement (their label); Purchase Agreement; Supply Agreement; Goods Supply Agreement

### Properties

appointment: no | commercial completeness: usually no

### Complexity

- The classifier's test against S1 is appointment plus programme children, never the title on
  the cover.

## S3. Framework purchase with releases

Buy-side framework with a versioned commercial layer; blanket POs or scheduling agreements sit
between framework and delivery, drawn down by releases. Forecasts hover at the edge of
bindingness and are recorded as evidence with a commitment band, not as orders.

```
Relationship: MillCo [relationship]
└── Supply agreement [master-level] {complete: yes}
    ├── (forms part of) Price list vN [component] ~> supersedes vN-1
    ├── (forms part of) Volume commitment [component]
    ├── (evidences) Rolling forecast [evidence] {non-binding band}
    └── (placed under) Blanket PO / scheduling agreement [order / transaction]
        └── (released under) Releases [order / transaction]
```

### Terminology

Master
: Supply Agreement; LTA; Long-Term Agreement; Framework Purchase Agreement

Order
: Blanket PO; Blanket Order; Scheduling Agreement; Release; Delivery Schedule; Firm Zone / Trade-off Zone Schedule

### Properties

commercial completeness: yes | forecast: binding band property | commitment: volume

### Complexity

- Forecast versus commitment is the family's recurring dispute; the binding band lives as a
  property on the forecast evidence node.

## S4. Software and cloud partner programmes, for resale

Click-through partner stacks for products we resell. Nearly everything incorporated by URL and
updated quarterly; the portal acceptance is the execution event. Strictly for resale: anything
consumed internally is V1 or V2, never this family.

```
Relationship: CloudVendorCo [relationship] {for resale}
└── Partner agreement v2026 [master-level] ~> supersedes v2025
    ├── (incorporates) Programme guide (URL) [shared / by reference]
    ├── (incorporates) Product and regional terms (URL) [shared / by reference]
    ├── (forms part of) DPA [component]
    └── (placed under) Portal orders [order / transaction] ~> resold under C-side
```

### Terminology

Master
: Partner Agreement; Cloud Solution Provider Agreement; CSP Agreement; Marketplace Programme Agreement; Reseller Programme Terms; Distribution Partner Terms

Shared terms
: Programme Guide; Product Terms; Service Terms; Regional Terms; Online Services Terms

### Properties

paper: theirs, click-through | update cadence: quarterly typical | execution event: portal
acceptance | purpose: resale only

### Complexity

- Version capture on every incorporates edge is the whole game; the terms you accepted are not
  the terms on the website today.
- Portal orders resold onward create back-to-back edges into customer families.

## S5. Commercial agency

Agency proper: we act as agent, title never passes, and statutory regimes bite, notably the EU
Commercial Agents Directive and Middle East agency protections with their termination
compensation and registration rules. Kept apart from S6 because the statutory regime changes the
risk profile of the whole family.

```
Relationship: PrincipalCo [relationship]
└── Agency agreement [master-level] {statutory regime: yes}
    ├── (forms part of) Territory and product schedules [component]
    ├── (forms part of) Commission schedule [component]
    └── (amends) Amendments [change]
```

### Terminology

Master
: Agency Agreement; Commercial Agency Agreement; Sales Agency Agreement; Sales Representative Agreement (check substance)

### Properties

statutory regime: EU CAD, Middle East agency law, other, none | title: never passes |
registration: jurisdiction dependent

### Complexity

- Termination is the event that matters; compensation and indemnity claims arise by statute
  regardless of the drafting.

## S6. Commission and introducer agreements

A fee for winning or introducing business, one-off or ongoing, often bringing local knowledge or
project expertise. No statutory agency regime, which is exactly why it is split from S5. Claims
reference the project or customer that earned them, another quiet cross-category edge.

```
Relationship: IntroducerCo [relationship]
└── Introducer agreement [master-level] {regime: none}
    ├── (forms part of) Project scope, commission terms [component]
    └── (claimed under) Commission claims [order / transaction] ~> references project / customer
```

### Terminology

Master
: Introducer Agreement; Commission Agreement; Finder's Fee Agreement; Referral Agreement; Business Development Agreement

### Properties

regime: none | duration: one-off or ongoing | anti-bribery diligence: flag

### Complexity

- The compliance risk is ABC-shaped, not agency-shaped; diligence evidence attaches through
  S12-style evidence nodes.

## S7. Manufacturing and private label

They make to our specification or under our brand. Specifications sit under change control and
version faster than the master; the quality agreement is owned by a different function; tooling
has its own title and lifecycle; a brand licence rides along where private label applies.

```
Relationship: FactoryCo [relationship]
└── Manufacturing and supply agreement [master-level]
    ├── (forms part of) Specifications vN [component] ~> change control
    ├── (forms part of) Quality agreement [component] {owner: quality}
    ├── (forms part of) Tooling agreement [component] {title: ours}
    ├── (forms part of) Brand licence [component]
    └── (placed under) Our POs [order / transaction]
```

### Terminology

Master
: Manufacturing and Supply Agreement; Contract Manufacturing Agreement; OEM Supply Agreement; Private Label Agreement; Toll Manufacturing Agreement

Component
: Specification; Technical Agreement; Quality Agreement; QAA; Tooling Agreement; Brand Licence; Trademark Licence

### Properties

spec control: change control process | tooling title: ours or theirs | brand licence: yes where
private label

### Complexity

- Three sub-documents with three different owners (commercial, quality, brand) under one
  master; ownership is a property worth recording.

## S8. Terms of purchase and supplier account forms

Mirror of C4 on the buy side. Our terms of purchase govern by default; the supplier's account
form or acknowledgement tries to bind us into theirs, and the conflict is recorded per order
with a last-shot property, never assumed at relationship level.

```
Relationship: PartsCo [relationship]
├── (governed by) Our terms of purchase vN [shared / by reference]
│   └── (placed under) Our PO [order / transaction]
│       └── (responds to) Their acknowledgement / quote [order / transaction] ~> conflicts with ToP
└── (rival instrument) Their supplier account form [master-level] ~> conflicts with ToP
```

### Terminology

Shared terms
: Terms of Purchase; Conditions of Purchase; General Purchasing Conditions; Standard Terms of Purchase

Rival anchor
: Supplier Account Form; New Supplier Form; Vendor Setup Form; Trading Terms Letter

### Properties

last shot: per order | rival anchor present: yes or no

### Complexity

- Their quote often fires first and our PO answers it, reversing the C4 sequence; direction of
  the responds-to edge captures which.

## S9. Special pricing and programme claims

High-volume, short-lived commercial instruments tied to a specific customer, project or product:
SPAs, deviated pricing, ship-and-debit, price protection, stock rotation, MDF and co-op,
rebates. Each links to the supplier relationship and to the specific customer relationship it
serves, which makes this the first family whose edges routinely cross categories. DPA here means
deviated pricing agreement, a collision with data processing that the alias registry
disambiguates.

```
Relationship: VendorCo [relationship]
├── SPA, customer Y, project X [change] {time-limited} ~> references C-relationship Y
│   └── (extends) Extension letter [change]
├── (claimed under) Ship-and-debit claims [order / transaction]
├── (claimed under) Price protection claims [order / transaction]
└── (claimed under) MDF / co-op claims [order / transaction]
```

### Terminology

Change
: SPA; Special Pricing Agreement; Deviated Pricing Agreement; DPA (deviated pricing sense); Meet-Comp; Contract Pricing Letter; Project Registration; Design Registration

Claims
: Ship-and-Debit Claim; S&D Claim; Debit Memo; Price Protection Claim; Stock Rotation Return; MDF Claim; Co-op Claim; Rebate Claim

### Properties

time-limited: yes | linked customer: relationship reference mandatory | claim settlement: credit
or debit memo

### Complexity

- Volume is the challenge: thousands of short-lived nodes; the cross edges to customer
  relationships are the analytical payoff.
- Every claim is a transaction node claimed under its instrument, which is what makes margin-
  recovery questions walkable.

## S10. Services for resale, back-to-back

Subcontracted services we resell. Supplier SOWs mirror customer SOWs, and the mismatches between
them (warranty period, liability cap, response times) are recorded as gap edges. The mirror and
gap edges into C6 are the family's purpose.

```
Relationship: SubcontractorCo [relationship]
└── Services partner agreement [master-level]
    ├── (forms part of) SLA, rate card [component]
    └── (agreed under) SOW (back-to-back) [work instrument] ~> mirrors C6 SOW, gap: warranty
        └── (placed under) Work orders [order / transaction]
```

### Terminology

Master
: Services Partner Agreement; Subcontract; Support Reseller Agreement; Installation Subcontract; Field Services Agreement

### Properties

mirror target: C6 SOW reference | gap register: per-term gap edges

### Complexity

- Each material term mismatch is one gap edge with the delta as a property; the set of gap
  edges is the risk register.

## S11. Supplier consignment and drop-ship

Their stock in our warehouse with title passing on our draw, or their delivery direct to our
customer. The physical flow bypasses us in drop-ship while the contract flow does not, and the
graph must keep the two apart.

```
Relationship: StockCo [relationship]
├── Consignment stock agreement [master-level] {title: theirs until draw}
│   ├── (forms part of) Stock schedule, settlement terms [component]
│   └── (evidences) Consumption reports [evidence]
└── (varies) Drop-ship addendum [change] ~> delivery direct to C-side
```

### Terminology

Master
: Consignment Stock Agreement; Vendor Consignment Agreement; Bonded Stock Agreement; Drop-Ship Agreement; Direct Ship Addendum

### Properties

title: theirs until draw | physical flow: through us or direct | settlement: on consumption

### Complexity

- Drop-ship creates delivery edges to customer sites while invoicing edges stay with us;
  conflating the two flows is the classic modelling error.

## S12. Quality and compliance evidence

Mostly evidence with validity periods rather than contracts: quality agreements aside, this is
declarations of conformity, REACH, RoHS and conflict minerals declarations, certificates of
conformity per batch, insurance certificates. Evidence attaches to products as well as to the
relationship and feeds importer and distributor obligations under product regulation.

```
Relationship: (any supplier) [relationship]
├── Quality agreement [master-level]
├── Code of conduct (ours, imposed) [master-level]
├── (evidences) DoC, CoC per batch [evidence] ~> attaches to product nodes
├── (evidences) REACH, RoHS, conflict minerals declarations [evidence]
└── (evidences) Insurance certificates [evidence] {validity window}
```

### Terminology

Evidence
: Declaration of Conformity; DoC; Certificate of Conformity; CoC; REACH Declaration; RoHS Declaration; CMRT; Conflict Minerals Report; Certificate of Insurance; COI; Test Report; Mill Certificate

### Properties

validity window: mandatory | attaches to: relationship and product | regulatory driver: importer
or distributor obligations

### Complexity

- Batch-level certificates attach to product nodes and even lots; expiry queries are the
  operational use case.

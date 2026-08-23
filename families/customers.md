# Customer families

13 families on the customer side. Each entry gives the family test, the tree, the terminology
that turns up on real cover pages, the classifying properties and the complexity that makes the
family worth separating.

## C1. Global master with local participation

This family exists where one negotiated agreement is intended to be adopted by multiple legal
entities, and adoption happens through a per-entity instrument, signed or deemed. The defining
structure is the participation layer sitting between the master and local trading. If that layer
exists the contract belongs here, whatever the cover page says and whoever's paper it is on. A
group agreement merely referenced by local entities with no adoption mechanism is C2 with scope
recorded as group-referenced.

```
Relationship: GlobalCo [relationship]
└── Global MSA 2021 [master-level] {scope: global, paper: ours, complete: no}
    ├── (forms part of) Sch 1 products [component]
    ├── (forms part of) Sch 2 pricing v3 [component] ~> supersedes v2
    ├── (forms part of) DPA [component]
    ├── (amends) Amendment 1 [change] ~> amends MSA cl.14
    ├── (varies) Side letter [change] {flow-down: per accession}
    ├── (accedes to) LPA Germany [participation] {status: signed}
    │   ├── (forms part of) Local sch A sites [component]
    │   ├── (amends) Local amendment 1 [change] ~> varies MSA cl.14
    │   └── (placed under) PO 4471 ... PO 9120 [order / transaction]
    └── (accedes to) LPA Netherlands [participation] {status: deemed}
        └── (placed under) POs [order / transaction]
```

### Terminology

Master
: MSA; Master Agreement; Master Supply Agreement; Master Sales Agreement; Global Master Agreement; Global Framework Agreement; Umbrella Agreement; on their paper: Master Purchase Agreement, Global Procurement Agreement, Supplier Agreement, Global Terms Agreement

Participation
: LPA; LIA; PA; MCA; Local Participation Agreement; Local Implementation Agreement; Participation Agreement; Master Country Agreement; Country Addendum; Accession Agreement; Adherence Agreement; Joinder; Affiliate Agreement; Local Country Agreement

Component
: Schedule; Annex; Exhibit; Appendix; Attachment

Change
: Amendment; Variation; Deed of Variation; Addendum (ambiguous); Side Letter

Order
: PO; Purchase Order; Order; Call-off; Order Acknowledgement

### Properties

scope: global | paper: ours or theirs | commercial completeness: no | participation status:
signed or deemed | flow-down: yes, no or per accession

### Complexity

- Two amendment chains, global and local, that drift apart; the accession edge carries the
  flow-down property, or each global amendment gets explicit flows-down-to edges to the LPAs
  that adopted it.
- Deemed participation (affiliates may order hereunder) still creates a participation node per
  entity, status deemed rather than signed.
- The varies edges from local amendments to master clauses are the highest-value edges in the
  family.

## C2. Negotiated master, single scope

One negotiated instrument carrying relationship terms (liability, warranty, compliance) for a
single legal entity or a group by loose reference, with commercials left to each transaction. No
participation layer and no self-executing commercial layer. Either paper: a customer-paper
procurement master is this family with paper recorded as theirs and its own alias set.

```
Relationship: RegionalCo [relationship]
└── Supply agreement 2020 [master-level] {scope: single, paper: theirs, complete: no}
    ├── (forms part of) Exhibit A pricing basis [component]
    ├── (incorporates) Code of conduct (URL) [shared / by reference] {captured 2024-06}
    ├── (amends) Addendum 1 [change]
    ├── (forms part of) Addendum 2 (new products) [component]
    └── (placed under) Quotation Q-310 [work instrument]
        └── (placed under) PO 8802 [order / transaction]
```

### Terminology

Master
: Supply Agreement; Sales Agreement; Master Purchase Agreement (their paper); Vendor Agreement (their label for us); Procurement Agreement; Trading Agreement; Commercial Agreement

Component
: Schedule; Annex; Exhibit; Appendix; Attachment; Policies and codes by URL

Change
: Addendum (both senses); Amendment; Variation; Deed of Variation; Addendum (ambiguous); Side Letter

### Properties

scope: single or group-referenced | paper: ours, theirs or hybrid | commercial completeness: no
| commitment: none to target

### Complexity

- The word Addendum names two different node types here: an amendment and a new component.
  Type is assigned by what the document does.
- URL-incorporated policies change without signature, so every incorporates edge carries
  version and capture date.

## C3. Framework with call-off

A master plus a versioned commercial layer (price list, blanket structure) that makes call-offs
self-executing: an order alone completes a contract on pre-agreed commercials. The test against
C2 is commercial completeness. Mostly customer paper in practice.

```
Relationship: MidCo [relationship]
└── Framework supply agreement 2019 [master-level] {complete: yes}
    ├── (forms part of) Price list 2025 [component] ~> supersedes 2023, 2021
    ├── (amends) Price adjustment letter 2022 [change] {indexed}
    ├── (extends) Extension letter 2024 [change] {+2 years}
    ├── (placed under) Blanket PO 1001 [order / transaction]
    │   └── (released under) Release 1, release 2 ... [order / transaction]
    └── (placed under) PO 2207 (standalone) [order / transaction]
```

### Terminology

Master
: Framework Agreement; Framework Supply Agreement; Pricing Agreement; Long-Term Agreement (LTA); Preferred Supplier Agreement; Blanket Order Agreement

Component
: Price List; Rate Schedule; Schedule; Annex; Exhibit; Appendix; Attachment

Change
: Price Adjustment Letter; Extension Letter; Amendment; Variation; Deed of Variation; Addendum (ambiguous); Side Letter

Order
: Blanket PO; Release; Call-off; PO; Purchase Order; Order; Call-off; Order Acknowledgement

### Properties

commercial completeness: yes | commitment: often volume or target | scope: usually single

### Complexity

- Almost all change happens in schedules and letters, not formal amendments; the supersedes
  chain on the price list is the family's spine.
- The blanket order inserts a level between framework and delivery: framework, blanket,
  release.

## C4. Account-based trading on standard terms

No negotiated master. Where a Customer Account Application Form (CAF) is in place it binds the
customer into our terms of sale and acts as a quasi-framework anchoring the account. Where it is
absent, each order is a battle of the forms resolved order by order. Customer Vendor
Registration Forms attempting the mirror move are recorded as rival instruments at the same
level. By volume this is the biggest family a distributor has.

```
Relationship: SmallCo [relationship]
├── CAF (account application) 2022 [master-level]
│   ├── (incorporates) Terms of sale v2023 [shared / by reference] ~> supersedes v2019
│   ├── (rival instrument) Their vendor registration form [master-level] ~> conflicts with CAF
│   └── (placed under) Quotation Q-5561 [work instrument]
│       └── (placed under) PO 77812 [order / transaction]
└── (no CAF:) PO 78001 (their terms) [order / transaction] ~> conflicts with ToS
    └── (responds to) Order acknowledgement [order / transaction] {last shot: ours}
```

### Terminology

Anchor
: CAF; Customer Account Application Form; Account Application; Account Opening Form; Credit Application; Trade Account Form; their side: Vendor Registration Form, Supplier Onboarding Form, Supplier Setup Form

Shared terms
: Terms of Sale; Terms and Conditions of Sale; Conditions of Sale; General Conditions; Standard Terms

Order
: Quotation; Quote; Proposal; PO; Purchase Order; Order; Call-off; Order Acknowledgement

### Properties

anchor present: yes or no | terms version in force: by order date | last shot: ours or theirs
per order

### Complexity

- Each order must point at the version of the shared terms in force on its date; the shared
  terms node has thousands of incoming edges, which is where the structure stops being a tree.
- Battle of the forms is a conflicts-with edge carrying a last-shot property, resolved per
  order, never per relationship.

## C5. Supply-chain and value-added services

Services that change or prepare the product itself: staging, kitting, cutting, configuration,
labelling, testing. Usually a schedule under a C1 to C3 master, sometimes a standalone VAS
agreement. Distinct from C6 because the deliverable is the modified product flowing through the
ordinary order stream, not a scoped project.

```
Relationship: (any customer) [relationship]
└── Master (C1 to C3) or standalone VAS agreement [master-level]
    ├── (forms part of) VAS schedule [component]
    │   ├── (forms part of) Kitting spec, cutting tolerances [component]
    │   └── (forms part of) Labelling and packaging spec [component]
    └── (placed under) POs [order / transaction] ~> reference VAS lines
```

### Terminology

Master or schedule
: VAS Agreement; Value-Added Services Schedule; Supply Chain Services Agreement; Kitting Agreement; Cutting Services Schedule; Configuration Services Schedule

Component
: Specification; Tolerances; Work Instruction; Schedule; Annex; Exhibit; Appendix; Attachment

### Properties

attachment: schedule under C1 to C3, or standalone | pricing: per line, per operation or bundled

### Complexity

- Specifications live under change control and version faster than the master; the supersedes
  chain sits at spec level.
- POs must reference the VAS lines, so the transaction layer carries edges into the schedule,
  not just the master.

## C6. General services and works

Services with a defined scope delivered as projects: installation, commissioning, design,
general contracting. The shape is master to SOW to change order, with pricing per SOW or quote;
rate cards are rare in distribution. Includes standalone SOWs for design work (racking layout,
wiring layout, assembly design) placed under standard terms with no master at all.

```
Relationship: ServiceCo [relationship]
├── Services MSA 2022 [master-level]
│   ├── (agreed under) SOW 1 racking design [work instrument]
│   │   ├── (amends) Change order 1 [change]
│   │   └── (evidences) Acceptance certificate [evidence]
│   └── (agreed under) SOW 2 installation [work instrument] {precedence: SOW}
└── Standalone SOW (system design) [work instrument] ~> incorporates ToS
```

### Terminology

Master
: Services MSA; Master Services Agreement; Professional Services Agreement; Installation Services Agreement

Work instrument
: SOW; Statement of Work; Work Order; Service Order; Task Order; Project Order

Change
: Change Order; Change Control Note; CCN; Variation; Amendment; Variation; Deed of Variation; Addendum (ambiguous); Side Letter

### Properties

precedence: per SOW (SOW over master or master over SOW) | pricing: per SOW or quote |
standalone SOW: incorporates shared terms

### Complexity

- Change orders amend the SOW, not the master; the SOW-versus-master precedence can differ per
  SOW and is a property, not an assumption.
- Installation work is typically subcontracted, which creates back-to-back edges into S10.

## C7. Industry model form projects

Project supply or subcontract on an industry model form: NEC, JCT, FIDIC with schedules of
amendments. Main-contract conditions are stepped down by incorporation, often without the
distributor ever holding the main contract, which is flagged on the incorporates edge. Bonds and
collateral warranties attach through the security overlay.

```
Relationship: MainContractorCo [relationship]
└── NEC subcontract [master-level] {paper: model form + amendments}
    ├── (incorporates) Main contract conditions [shared / by reference] {held: no, flag}
    ├── (forms part of) Scope, programme, BoM schedules [component]
    ├── (amends) Variation order 1, 2 [change]
    ├── (secured by) Performance bond, collateral warranty [security] ~> security overlay O1
    └── (placed under) Call-offs / POs [order / transaction]
```

### Terminology

Master
: NEC Subcontract; JCT Subcontract; FIDIC Subcontract; Works Order; Project Supply Agreement; Trade Contract

Change
: Variation Order; Compensation Event; Variation Instruction; Amendment; Variation; Deed of Variation; Addendum (ambiguous); Side Letter

Security
: Performance Bond; Advance Payment Bond; Retention Bond; Collateral Warranty; Parent Company Guarantee

### Properties

paper: model form | model form: NEC, JCT, FIDIC, other | main contract held: yes or no

### Complexity

- The incorporated main-contract conditions may not be in the file; the flag on the edge is
  the risk register entry.
- Bonds and warranties have their own lifecycle (expiry, release, calls) independent of the
  subcontract.

## C8. EPC exceptions pattern

An EPC contractor puts its terms in front of us at bid stage and asks for a list of exceptions.
The exceptions and clarifications list, in whatever form it takes, is memorialised in special
conditions. The executed instrument is a layered, pre-agreed PO incorporating general
conditions, special conditions prevailing over them, and a body of technical exhibits. The
family question is whether the exceptions list survives as its own instrument or merges into the
special conditions; this model keeps it alive as a node with a memorialised-in edge.

```
Relationship: EPCCo [relationship]
├── Exceptions and clarifications list [change] ~> memorialised in SC
└── PO (layered, pre-agreed) [order / transaction]
    ├── (incorporates) General conditions (theirs) [shared / by reference]
    ├── (incorporates) Special conditions [component] ~> prevails over GC
    └── (incorporates) Technical exhibits and schedules [component]
```

### Terminology

Bid layer
: Exceptions List; Exceptions and Clarifications; Deviations List; Comments Sheet; Bid Qualifications

Conditions
: General Conditions; GC; General Terms and Conditions of Purchase; Special Conditions; SC; Particular Conditions; Supplementary Conditions

Order
: Purchase Order; PO; Contract Order; Supply Contract

### Properties

paper: theirs | precedence chain: SC over GC over exhibits (verify per deal) | exceptions list:
survives or merged

### Complexity

- The PO is the execution event for the whole stack, so its incorporates edges carry the
  entire contract.
- Prevails-over edges matter more than the tree here; a wrong precedence chain is the family's
  characteristic failure.

## C9. Consignment, VMI, DLF and integrated supply

Our stock held at the customer's site with title passing on consumption. VMI adds our management
of replenishment; DLF (direct line feed) adds our personnel on site filling bins, racks or any
other min/max system. Integrated supply and in-plant store variants extend the same shape. The
defining structure is site schedules and min/max lists changing monthly under a stable master,
settled against consumption reports.

```
Relationship: PlantCo [relationship]
└── Consignment / VMI / DLF agreement [master-level] {on-site labour: DLF only}
    ├── (forms part of) Site schedule per location [component]
    ├── (forms part of) Min/max bin list [component] ~> supersedes monthly
    ├── (forms part of) Replenishment and buy-back terms [component]
    └── (evidences) Consumption reports [evidence]
        └── (settled by) Invoices [order / transaction]
```

### Terminology

Master
: Consignment Agreement; Consignment Stock Agreement; VMI Agreement; Vendor Managed Inventory Agreement; DLF Agreement; Direct Line Feed Agreement; In-Plant Store Agreement; Integrated Supply Agreement; Stocking Agreement

Component
: Site Schedule; Bin List; Min/Max List; Replenishment Plan; Buy-Back Terms

### Properties

title transfer: on consumption | on-site labour: none, VMI-managed or DLF | site link: covers-
site edges into master data

### Complexity

- The min/max list supersedes monthly; treat it as a versioned component or the graph drowns
  in amendments.
- Site schedules carry covers-site edges into master data, which is what makes site-level
  questions answerable.

## C10. Reseller and sub-distributor

The customer resells onward. Territory and product schedules constrain the appointment, and
vendor end-user terms flow down through us into the customer's tree, which creates deliberate
edges from S1 shared nodes into this family.

```
Relationship: DealerCo [relationship]
└── Reseller agreement [master-level]
    ├── (forms part of) Territory and product schedules [component]
    ├── (incorporates) Vendor end-user terms [shared / by reference] ~> flows down from S1
    └── (placed under) POs [order / transaction]
```

### Terminology

Master
: Reseller Agreement; Dealer Agreement; Sub-Distribution Agreement; Sub-Distributor Agreement; Partner Agreement; Channel Agreement

### Properties

appointment: yes (by us) | territory and product constraints: schedule level | flow-down source:
S1 family

### Complexity

- The flows-down-to edges from vendor terms are cross-category and cross-relationship; they
  are exactly what a folder structure cannot show.

## C11. Public sector frameworks

An awarded framework that is not itself a contract to supply; each authority's call-off is.
Authorities fan out under the framework like LPAs under a master. Lots and call-offs are UK-
flavoured terminology; the structure travels across jurisdictions even where the names do not,
so jurisdiction is a property, and OCDS is available as an optional adapter.

```
Relationship: Authority framework [relationship] {jurisdiction: UK}
└── Framework agreement [master-level]
    └── (forms part of) Lot 2 [component]
        ├── (called off under) Call-off contract, authority A [master-level]
        │   └── (placed under) Order form [work instrument]
        │       └── (placed under) POs [order / transaction]
        └── (called off under) Call-off contract, authority B [master-level]
```

### Terminology

Master
: Framework Agreement; Dynamic Purchasing System; DPS; Panel Arrangement; Standing Offer; IDIQ (US flavour)

Call-off
: Call-off Contract; Order Contract; Mini-Competition Award; Task Order; Standing Offer Call-up

### Properties

jurisdiction: ISO 3166 | lot structure: yes or no | call-off basis: direct award or mini-
competition

### Complexity

- The framework alone creates no supply obligation; agents must not treat it as a governing
  master for orders that lack a call-off.
- Each calling-off authority is a distinct legal entity with its own party edges into master
  data.

## C12. E-commerce accounts

A registered web account governed by webshop terms, standard or negotiated; users attach to the
account and orders attach through it. Distinct from EDI, API and PunchOut, which are channels
usually documented as a schedule inside another family (overlay O5) because an underlying
contract is typically negotiated. Agent-based ordering is a reserved future channel type.

```
Relationship: WebBuyerCo [relationship]
└── E-commerce account [master-level] {master data link}
    ├── (governed by) Webshop terms v2026 [shared / by reference] ~> or negotiated agreement
    ├── (attached to) Users (authorised buyers) [evidence]
    └── (placed under) Web orders [order / transaction]
```

### Terminology

Anchor
: E-commerce Account; Web Account; Online Trade Account; Customer Portal Account

Shared terms
: Website Terms; Webshop Terms; Online Terms of Sale; E-commerce Terms and Conditions

### Properties

terms: standard or negotiated | users: person nodes with user-of edges | channel overlays: O5
where EDI, API or PunchOut added

### Complexity

- Click-accept is the execution event; capture date and version matter more than signature.
- Thousands of accounts share one terms node, the same many-to-one shape as C4.

## C13. Programmes and pricing letters

Annual or project-specific commercial letters that vary pricing under whatever else governs:
rebates, growth incentives, special pricing letters. Re-issue supersedes; project letters are
time-limited. They attach to the relationship and reference the governing master or price list
where one exists.

```
Relationship: KeyAccountCo [relationship]
├── Rebate letter 2026 [change] ~> supersedes 2025
│   └── (forms part of) Targets schedule [component]
├── Growth incentive letter [change]
└── Special pricing letter, project X [change] {time-limited} ~> varies price list
```

### Terminology

Change
: Rebate Letter; Rebate Agreement; Growth Incentive Letter; Special Pricing Letter; Pricing Letter; SPA (customer-side sense); Project Pricing Letter

### Properties

cycle: annual re-issue or project | time-limited: usually yes | varies: master or price list

### Complexity

- Annual re-issue makes the supersedes chain the family's backbone; the current letter is a
  point-in-time query, not a folder.
- SPA collides with the supplier-side S9 sense and with Sale and Purchase Agreement; the alias
  registry disambiguates by category.

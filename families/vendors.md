# Vendor families

11 families on the vendor side. Each entry gives the family test, the tree, the terminology that
turns up on real cover pages, the classifying properties and the complexity that makes the
family worth separating.

## V1. SaaS subscriptions

Own-consumption cloud software. The operative commercial instrument is the order form; the
master sits above it by URL reference and can change; the negotiated security addendum prevails
over the URL terms. Renewal order forms supersede their predecessors.

```
Relationship: SaaSCo [relationship]
└── MSA (URL) v2026 [shared / by reference] ~> mutable master
    ├── (placed under) Order form 2 [work instrument] ~> renewal, supersedes OF1
    ├── (forms part of) DPA + SCCs [component] {subprocessors: URL}
    ├── (incorporates) SLA, support, AUP (URL) [shared / by reference]
    └── (forms part of) Security addendum (signed) [component] ~> prevails over URL terms
```

### Terminology

Master
: MSA; Master Subscription Agreement; Cloud Services Agreement; Terms of Service; ToS; Online Services Agreement

Work instrument
: Order Form; Order Schedule; Subscription Order; Quote (executed)

### Properties

master: by URL, mutable, capture dates mandatory | operative instrument: order form |
precedence: signed addendum over URL terms

### Complexity

- Every URL incorporation carries version and capture date; the subprocessor list changes on
  notice and needs its own capture trail.

## V2. Enterprise licence and support

Perpetual or term licences with annual support renewals forming a chain of new instruments, plus
audit and true-up letters that amend the licensed position.

```
Relationship: SoftwareCo [relationship]
└── Licence agreement [master-level]
    ├── (forms part of) Licence schedules [component]
    ├── (renews under) Annual support renewal 2026 [work instrument] ~> chain: 2024, 2025
    └── (amends) True-up letter [change]
```

### Terminology

Master
: Licence Agreement; Software Licence Agreement; EULA; Volume Licensing Agreement; Enterprise Agreement

Renewal
: Support Renewal; Maintenance Renewal; Support and Maintenance Order; True-Up Order

### Properties

renewals: new instruments in a chain | true-ups: amendments | audit rights: flag

### Complexity

- Renewals are instruments, not status flips; the chain answers what was supported when.

## V3. IT services and outsourcing

Long-term managed services: master, many SOWs with independent lifecycles, service levels, exit
plan, formal change control producing change notes.

```
Relationship: MSPCo [relationship]
└── Services MSA [master-level]
    ├── (agreed under) SOW 1, SOW 2 [work instrument] {independent lifecycles}
    │   └── (amends) Change notes [change]
    └── (forms part of) Service levels, exit plan [component]
```

### Terminology

Master
: Managed Services Agreement; IT Services Agreement; Outsourcing Agreement; Master Services Agreement

Change
: Change Note; Change Request; CR; Change Control Note; Contract Change Note

### Properties

exit plan: component with its own review cycle | SOW precedence: per SOW

### Complexity

- Exit is the family's tail risk; the exit plan node and its currency deserve monitoring
  edges.

## V4. Telecoms and connectivity

A master with hundreds of small service orders per site or circuit, each with its own minimum
term and auto-renewal. The population of orders, not the master, is where the money and the
notice deadlines live.

```
Relationship: TelcoCo [relationship]
└── Master services agreement [master-level]
    └── (placed under) Service orders per site / circuit [work instrument] {auto-renew, min terms}
```

### Terminology

Work instrument
: Service Order; Circuit Order; Connection Order; Site Order

### Properties

auto-renew: per order | minimum term: per order | notice window: per order

### Complexity

- Renewal-notice queries run across the order population; the master is almost never the
  answer.

## V5. Professional advisers

Panel terms or outside counsel guidelines on our paper prevailing over the adviser's terms of
business, with an engagement letter per matter and fee letters varying it. The adviser's own
terms are incorporated and periodically updated.

```
Relationship: LawFirmLLP [relationship]
└── Panel terms / outside counsel guidelines [master-level] ~> prevail over their ToB
    ├── (incorporates) Their terms of business vN [shared / by reference]
    └── (engaged under) Engagement letter per matter [work instrument]
        └── (varies) Fee letters, scope changes [change]
```

### Terminology

Master
: Panel Agreement; Panel Terms; Outside Counsel Guidelines; OCG; Framework Engagement Terms

Work instrument
: Engagement Letter; Letter of Engagement; Retainer Letter; Terms of Engagement; Matter Confirmation

### Properties

precedence: our guidelines over their ToB | granularity: one engagement per matter

### Complexity

- Matter-level engagement letters map one-to-one onto matters in practice management, a
  natural join to a different master data set.

## V6. Recruitment, staffing and contractors

Agency terms of business with assignment schedules, consultancy agreements with SOWs, employer
of record arrangements with country addenda. Introduction fees and off-payroll status are the
recurring properties. Employment contracts are out of scope, a people category to decide
separately.

```
Relationship: AgencyCo [relationship]
├── Agency terms of business [master-level]
│   └── (placed under) Assignment schedules [work instrument]
└── Consultancy agreement [master-level]
    └── (agreed under) SOWs [work instrument] {off-payroll status}
```

### Terminology

Master
: Terms of Business; ToB; Recruitment Agency Terms; Consultancy Agreement; Contractor Agreement; Employer of Record Agreement; Umbrella Company Terms

Work instrument
: Assignment Schedule; Placement Confirmation; Assignment Confirmation; SOW

### Properties

introduction fee: window and amount | off-payroll: status per engagement

### Complexity

- Assignment schedules carry person references, joining contract data to people data with the
  obvious privacy overlay.

## V7. Property

Agreement for lease into lease, then a long life of deeds and consents: rent deposit deed,
licences to alter, assign or sublet, deeds of variation, personal side letters, rent review
memoranda, break notices, subleases. Deeds, statutory overlay and decade-scale lifecycles make
this the slowest family in the graph.

```
Relationship: LandlordCo [relationship]
└── Agreement for lease [master-level]
    └── (granted under) Lease [master-level] {deed, long life}
        ├── (forms part of) Rent deposit deed [component]
        ├── (consented under) Licences to alter / assign / sublet [component]
        ├── (varies) Deed of variation, side letter [change] {side letter: personal}
        ├── (evidences) Rent review memorandum [evidence]
        ├── (terminates) Break notice [change]
        └── (granted under) Sublease [master-level]
```

### Terminology

Master
: Agreement for Lease; AfL; Lease; Underlease; Sublease; Licence to Occupy; Reversionary Lease; Wayleave; Heads of Terms (pre-contract)

Change
: Deed of Variation; Side Letter; Rent Review Memorandum; Licence to Alter; Licence to Assign; Break Notice

### Properties

instrument form: deed | side letters: personal, non-transferable flag | statutory overlay:
jurisdiction

### Complexity

- Personal side letters do not bind successors; the personal flag changes what a due diligence
  walk may rely on.

## V8. Facilities and equipment

Master hire or lease with equipment schedules per asset, acceptance certificates, extensions and
returns, plus FM contracts with site schedules and SLAs. The master-plus-schedules shape is the
C1 pattern wearing overalls.

```
Relationship: HireCo [relationship]
└── Master lease / hire agreement [master-level]
    ├── (placed under) Equipment schedule per asset [work instrument]
    │   ├── (evidences) Acceptance certificate [evidence]
    │   └── (extends) Extension / return note [change]
    └── (forms part of) FM site schedules, SLAs [component]
```

### Terminology

Master
: Master Lease; Master Hire Agreement; Equipment Lease; Hire Purchase Agreement; FM Contract; Facilities Management Agreement

Work instrument
: Equipment Schedule; Asset Schedule; Hire Schedule

### Properties

per-asset schedules: one node per asset | acceptance: evidence gate for payment

### Complexity

- Asset schedules join to fixed-asset registers, another master data set outside this spine
  but linkable by the same discipline.

## V9. Logistics and fleet

Logistics services agreements with versioned rate cards, lane and site schedules, KPI schedules
and annual rate letters; carrier agreements incorporating standard carrier conditions with their
own liability limits; customs brokerage; fleet master leases. Borderline by design: the cost is
recharged to customers but the service is consumed by us, so vendor.

```
Relationship: 3PLCo [relationship] {cost recharged, service consumed by us}
└── Logistics services agreement [master-level]
    ├── (forms part of) Rate card vN, lane and site schedules [component] ~> supersedes annually
    ├── (incorporates) Standard carrier conditions [shared / by reference] {own liability limits}
    └── (varies) Annual rate letters [change]
```

### Terminology

Master
: Logistics Services Agreement; 3PL Agreement; Warehousing Agreement; Carriage Agreement; Freight Agreement; Customs Brokerage Agreement; Fleet Lease

Shared terms
: RHA Conditions; BIFA Conditions; CMR; standard carrier conditions generally

### Properties

incorporated conditions: liability limits recorded | rate cycle: annual

### Complexity

- Incorporated carrier conditions cap liability far below cargo value; the limit belongs on
  the incorporates edge where an agent will trip over it.

## V10. Banking, finance and insurance

Facility agreements with security documents cutting across group entities, compliance
certificates, amendments and waivers; insurance policies with schedules, endorsements and
renewals; credit insurance whose buyer limits point at customer master data, a deliberate cross-
category edge. Lumped as one family for now; splitting finance from insurance is a known
candidate refinement.

```
Relationship: BankCo / InsurerCo [relationship]
├── Facility agreement [master-level]
│   ├── (secured by) Debenture, charges [security] ~> cross group entities
│   ├── (evidences) Compliance certificates [evidence]
│   └── (amends) Amendments and waivers [change]
└── Insurance policy [master-level]
    ├── (forms part of) Schedule [component]
    ├── (amends) Endorsements, renewals [change]
    └── (forms part of) Credit insurance buyer limits [component] ~> points at customer master data
```

### Terminology

Master
: Facility Agreement; RCF; Revolving Credit Facility; Invoice Finance Agreement; ISDA Master Agreement; Insurance Policy; Credit Insurance Policy

Security
: Debenture; Charge; Guarantee; Intercreditor Agreement; Security Agreement

Change
: Amendment and Waiver; Endorsement; Renewal Schedule

### Properties

security scope: entities charged | buyer limits: per customer account | covenant evidence:
certificate cycle

### Complexity

- Security documents bind entities that never trade with the counterparty; the party edges are
  the point.
- Credit insurance buyer limits are vendor-category nodes pointing at customer accounts, the
  graph's most useful cross-category edge for credit control.

## V11. Indirect goods and services

The long tail: terms of purchase, PO, invoice, mostly auto-renewing, individually small and
collectively noisy. Marketing agencies, sponsorships, memberships, data subscriptions, travel,
utilities. Low modelling depth by design: invariant edges, dates and renewal flags.

```
Relationship: (misc vendors) [relationship]
└── (governed by) Terms of purchase vN [shared / by reference]
    └── (placed under) PO [order / transaction]
        └── (settled by) Invoice [order / transaction] {auto-renew, high volume}
```

### Terminology

Master
: Terms of Purchase; Order Form; Subscription Agreement; Membership Terms; Sponsorship Agreement; Media Buying Terms

### Properties

modelling depth: minimal | renewal: auto flags and dates

### Complexity

- The catch-all discipline matters most here: function tags and invariant edges even where
  family confidence is low.

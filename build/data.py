# Distributor Contract Graph v0.1 - single source data module.
# Tree tuples: (depth, edge_label, edge_kind, node_label, node_type, xref, prop)
# edge_kind: s=structural, l=lifecycle, t=transactional, e=evidence, ''=root/none
# node types: rel, master, part, comp, ch, wk, ord, sh, ev, sec

VERSION = "0.1.0"

NODE_TYPE_NAMES = {
    "rel": "relationship", "master": "master-level", "part": "participation",
    "comp": "component", "ch": "change", "wk": "work instrument",
    "ord": "order / transaction", "sh": "shared / by reference",
    "ev": "evidence", "sec": "security",
}

GEN_COMPONENT = ["Schedule", "Annex", "Exhibit", "Appendix", "Attachment"]
GEN_CHANGE = ["Amendment", "Variation", "Deed of Variation", "Addendum (ambiguous)", "Side Letter"]
GEN_ORDER = ["PO", "Purchase Order", "Order", "Call-off", "Order Acknowledgement"]

FAMILIES = [
# ---------------- CUSTOMERS ----------------
dict(code="C1", cat="Customers", name="Global master with local participation",
 test=("This family exists where one negotiated agreement is intended to be adopted by multiple "
   "legal entities, and adoption happens through a per-entity instrument, signed or deemed. The "
   "defining structure is the participation layer sitting between the master and local trading. "
   "If that layer exists the contract belongs here, whatever the cover page says and whoever's "
   "paper it is on. A group agreement merely referenced by local entities with no adoption "
   "mechanism is C2 with scope recorded as group-referenced."),
 tree=[(0,"","","Relationship: GlobalCo","rel","",""),
  (1,"","","Global MSA 2021","master","","scope: global, paper: ours, complete: no"),
  (2,"forms part of","s","Sch 1 products","comp","",""),
  (2,"forms part of","s","Sch 2 pricing v3","comp","supersedes v2",""),
  (2,"forms part of","s","DPA","comp","",""),
  (2,"amends","l","Amendment 1","ch","amends MSA cl.14",""),
  (2,"varies","l","Side letter","ch","","flow-down: per accession"),
  (2,"accedes to","s","LPA Germany","part","","status: signed"),
  (3,"forms part of","s","Local sch A sites","comp","",""),
  (3,"amends","l","Local amendment 1","ch","varies MSA cl.14",""),
  (3,"placed under","t","PO 4471 ... PO 9120","ord","",""),
  (2,"accedes to","s","LPA Netherlands","part","","status: deemed"),
  (3,"placed under","t","POs","ord","","")],
 terms=[("Master","MSA; Master Agreement; Master Supply Agreement; Master Sales Agreement; Global Master Agreement; Global Framework Agreement; Umbrella Agreement; on their paper: Master Purchase Agreement, Global Procurement Agreement, Supplier Agreement, Global Terms Agreement"),
  ("Participation","LPA; LIA; PA; MCA; Local Participation Agreement; Local Implementation Agreement; Participation Agreement; Master Country Agreement; Country Addendum; Accession Agreement; Adherence Agreement; Joinder; Affiliate Agreement; Local Country Agreement"),
  ("Component","; ".join(GEN_COMPONENT)),
  ("Change","; ".join(GEN_CHANGE)),
  ("Order","; ".join(GEN_ORDER))],
 props="scope: global | paper: ours or theirs | commercial completeness: no | participation status: signed or deemed | flow-down: yes, no or per accession",
 complexity=["Two amendment chains, global and local, that drift apart; the accession edge carries the flow-down property, or each global amendment gets explicit flows-down-to edges to the LPAs that adopted it.",
  "Deemed participation (affiliates may order hereunder) still creates a participation node per entity, status deemed rather than signed.",
  "The varies edges from local amendments to master clauses are the highest-value edges in the family."]),

dict(code="C2", cat="Customers", name="Negotiated master, single scope",
 test=("One negotiated instrument carrying relationship terms (liability, warranty, compliance) for a "
   "single legal entity or a group by loose reference, with commercials left to each transaction. "
   "No participation layer and no self-executing commercial layer. Either paper: a customer-paper "
   "procurement master is this family with paper recorded as theirs and its own alias set."),
 tree=[(0,"","","Relationship: RegionalCo","rel","",""),
  (1,"","","Supply agreement 2020","master","","scope: single, paper: theirs, complete: no"),
  (2,"forms part of","s","Exhibit A pricing basis","comp","",""),
  (2,"incorporates","s","Code of conduct (URL)","sh","","captured 2024-06"),
  (2,"amends","l","Addendum 1","ch","",""),
  (2,"forms part of","s","Addendum 2 (new products)","comp","",""),
  (2,"placed under","t","Quotation Q-310","wk","",""),
  (3,"placed under","t","PO 8802","ord","","")],
 terms=[("Master","Supply Agreement; Sales Agreement; Master Purchase Agreement (their paper); Vendor Agreement (their label for us); Procurement Agreement; Trading Agreement; Commercial Agreement"),
  ("Component","; ".join(GEN_COMPONENT) + "; Policies and codes by URL"),
  ("Change","Addendum (both senses); " + "; ".join(GEN_CHANGE))],
 props="scope: single or group-referenced | paper: ours, theirs or hybrid | commercial completeness: no | commitment: none to target",
 complexity=["The word Addendum names two different node types here: an amendment and a new component. Type is assigned by what the document does.",
  "URL-incorporated policies change without signature, so every incorporates edge carries version and capture date."]),

dict(code="C3", cat="Customers", name="Framework with call-off",
 test=("A master plus a versioned commercial layer (price list, blanket structure) that makes call-offs "
   "self-executing: an order alone completes a contract on pre-agreed commercials. The test against C2 "
   "is commercial completeness. Mostly customer paper in practice."),
 tree=[(0,"","","Relationship: MidCo","rel","",""),
  (1,"","","Framework supply agreement 2019","master","","complete: yes"),
  (2,"forms part of","s","Price list 2025","comp","supersedes 2023, 2021",""),
  (2,"amends","l","Price adjustment letter 2022","ch","","indexed"),
  (2,"extends","l","Extension letter 2024","ch","","+2 years"),
  (2,"placed under","t","Blanket PO 1001","ord","",""),
  (3,"released under","t","Release 1, release 2 ...","ord","",""),
  (2,"placed under","t","PO 2207 (standalone)","ord","","")],
 terms=[("Master","Framework Agreement; Framework Supply Agreement; Pricing Agreement; Long-Term Agreement (LTA); Preferred Supplier Agreement; Blanket Order Agreement"),
  ("Component","Price List; Rate Schedule; " + "; ".join(GEN_COMPONENT)),
  ("Change","Price Adjustment Letter; Extension Letter; " + "; ".join(GEN_CHANGE)),
  ("Order","Blanket PO; Release; Call-off; " + "; ".join(GEN_ORDER))],
 props="commercial completeness: yes | commitment: often volume or target | scope: usually single",
 complexity=["Almost all change happens in schedules and letters, not formal amendments; the supersedes chain on the price list is the family's spine.",
  "The blanket order inserts a level between framework and delivery: framework, blanket, release."]),

dict(code="C4", cat="Customers", name="Account-based trading on standard terms",
 test=("No negotiated master. Where a Customer Account Application Form (CAF) is in place it binds the "
   "customer into our terms of sale and acts as a quasi-framework anchoring the account. Where it is "
   "absent, each order is a battle of the forms resolved order by order. Customer Vendor Registration "
   "Forms attempting the mirror move are recorded as rival instruments at the same level. By volume "
   "this is the biggest family a distributor has."),
 tree=[(0,"","","Relationship: SmallCo","rel","",""),
  (1,"","","CAF (account application) 2022","master","",""),
  (2,"incorporates","s","Terms of sale v2023","sh","supersedes v2019",""),
  (2,"rival instrument","s","Their vendor registration form","master","conflicts with CAF",""),
  (2,"placed under","t","Quotation Q-5561","wk","",""),
  (3,"placed under","t","PO 77812","ord","",""),
  (1,"no CAF:","","PO 78001 (their terms)","ord","conflicts with ToS",""),
  (2,"responds to","t","Order acknowledgement","ord","","last shot: ours")],
 terms=[("Anchor","CAF; Customer Account Application Form; Account Application; Account Opening Form; Credit Application; Trade Account Form; their side: Vendor Registration Form, Supplier Onboarding Form, Supplier Setup Form"),
  ("Shared terms","Terms of Sale; Terms and Conditions of Sale; Conditions of Sale; General Conditions; Standard Terms"),
  ("Order","Quotation; Quote; Proposal; " + "; ".join(GEN_ORDER))],
 props="anchor present: yes or no | terms version in force: by order date | last shot: ours or theirs per order",
 complexity=["Each order must point at the version of the shared terms in force on its date; the shared terms node has thousands of incoming edges, which is where the structure stops being a tree.",
  "Battle of the forms is a conflicts-with edge carrying a last-shot property, resolved per order, never per relationship."]),

dict(code="C5", cat="Customers", name="Supply-chain and value-added services",
 test=("Services that change or prepare the product itself: staging, kitting, cutting, configuration, "
   "labelling, testing. Usually a schedule under a C1 to C3 master, sometimes a standalone VAS "
   "agreement. Distinct from C6 because the deliverable is the modified product flowing through the "
   "ordinary order stream, not a scoped project."),
 tree=[(0,"","","Relationship: (any customer)","rel","",""),
  (1,"","","Master (C1 to C3) or standalone VAS agreement","master","",""),
  (2,"forms part of","s","VAS schedule","comp","",""),
  (3,"forms part of","s","Kitting spec, cutting tolerances","comp","",""),
  (3,"forms part of","s","Labelling and packaging spec","comp","",""),
  (2,"placed under","t","POs","ord","reference VAS lines","")],
 terms=[("Master or schedule","VAS Agreement; Value-Added Services Schedule; Supply Chain Services Agreement; Kitting Agreement; Cutting Services Schedule; Configuration Services Schedule"),
  ("Component","Specification; Tolerances; Work Instruction; " + "; ".join(GEN_COMPONENT))],
 props="attachment: schedule under C1 to C3, or standalone | pricing: per line, per operation or bundled",
 complexity=["Specifications live under change control and version faster than the master; the supersedes chain sits at spec level.",
  "POs must reference the VAS lines, so the transaction layer carries edges into the schedule, not just the master."]),

dict(code="C6", cat="Customers", name="General services and works",
 test=("Services with a defined scope delivered as projects: installation, commissioning, design, general "
   "contracting. The shape is master to SOW to change order, with pricing per SOW or quote; rate cards "
   "are rare in distribution. Includes standalone SOWs for design work (racking layout, wiring layout, "
   "assembly design) placed under standard terms with no master at all."),
 tree=[(0,"","","Relationship: ServiceCo","rel","",""),
  (1,"","","Services MSA 2022","master","",""),
  (2,"agreed under","s","SOW 1 racking design","wk","",""),
  (3,"amends","l","Change order 1","ch","",""),
  (3,"evidences","e","Acceptance certificate","ev","",""),
  (2,"agreed under","s","SOW 2 installation","wk","","precedence: SOW"),
  (1,"","","Standalone SOW (system design)","wk","incorporates ToS","")],
 terms=[("Master","Services MSA; Master Services Agreement; Professional Services Agreement; Installation Services Agreement"),
  ("Work instrument","SOW; Statement of Work; Work Order; Service Order; Task Order; Project Order"),
  ("Change","Change Order; Change Control Note; CCN; Variation; " + "; ".join(GEN_CHANGE))],
 props="precedence: per SOW (SOW over master or master over SOW) | pricing: per SOW or quote | standalone SOW: incorporates shared terms",
 complexity=["Change orders amend the SOW, not the master; the SOW-versus-master precedence can differ per SOW and is a property, not an assumption.",
  "Installation work is typically subcontracted, which creates back-to-back edges into S10."]),

dict(code="C7", cat="Customers", name="Industry model form projects",
 test=("Project supply or subcontract on an industry model form: NEC, JCT, FIDIC with schedules of "
   "amendments. Main-contract conditions are stepped down by incorporation, often without the "
   "distributor ever holding the main contract, which is flagged on the incorporates edge. Bonds and "
   "collateral warranties attach through the security overlay."),
 tree=[(0,"","","Relationship: MainContractorCo","rel","",""),
  (1,"","","NEC subcontract","master","","paper: model form + amendments"),
  (2,"incorporates","s","Main contract conditions","sh","","held: no, flag"),
  (2,"forms part of","s","Scope, programme, BoM schedules","comp","",""),
  (2,"amends","l","Variation order 1, 2","ch","",""),
  (2,"secured by","e","Performance bond, collateral warranty","sec","security overlay O1",""),
  (2,"placed under","t","Call-offs / POs","ord","","")],
 terms=[("Master","NEC Subcontract; JCT Subcontract; FIDIC Subcontract; Works Order; Project Supply Agreement; Trade Contract"),
  ("Change","Variation Order; Compensation Event; Variation Instruction; " + "; ".join(GEN_CHANGE)),
  ("Security","Performance Bond; Advance Payment Bond; Retention Bond; Collateral Warranty; Parent Company Guarantee")],
 props="paper: model form | model form: NEC, JCT, FIDIC, other | main contract held: yes or no",
 complexity=["The incorporated main-contract conditions may not be in the file; the flag on the edge is the risk register entry.",
  "Bonds and warranties have their own lifecycle (expiry, release, calls) independent of the subcontract."]),

dict(code="C8", cat="Customers", name="EPC exceptions pattern",
 test=("An EPC contractor puts its terms in front of us at bid stage and asks for a list of exceptions. "
   "The exceptions and clarifications list, in whatever form it takes, is memorialised in special "
   "conditions. The executed instrument is a layered, pre-agreed PO incorporating general conditions, "
   "special conditions prevailing over them, and a body of technical exhibits. The family question is "
   "whether the exceptions list survives as its own instrument or merges into the special conditions; "
   "this model keeps it alive as a node with a memorialised-in edge."),
 tree=[(0,"","","Relationship: EPCCo","rel","",""),
  (1,"","","Exceptions and clarifications list","ch","memorialised in SC",""),
  (1,"","","PO (layered, pre-agreed)","ord","",""),
  (2,"incorporates","s","General conditions (theirs)","sh","",""),
  (2,"incorporates","s","Special conditions","comp","prevails over GC",""),
  (2,"incorporates","s","Technical exhibits and schedules","comp","","")],
 terms=[("Bid layer","Exceptions List; Exceptions and Clarifications; Deviations List; Comments Sheet; Bid Qualifications"),
  ("Conditions","General Conditions; GC; General Terms and Conditions of Purchase; Special Conditions; SC; Particular Conditions; Supplementary Conditions"),
  ("Order","Purchase Order; PO; Contract Order; Supply Contract")],
 props="paper: theirs | precedence chain: SC over GC over exhibits (verify per deal) | exceptions list: survives or merged",
 complexity=["The PO is the execution event for the whole stack, so its incorporates edges carry the entire contract.",
  "Prevails-over edges matter more than the tree here; a wrong precedence chain is the family's characteristic failure."]),

dict(code="C9", cat="Customers", name="Consignment, VMI, DLF and integrated supply",
 test=("Our stock held at the customer's site with title passing on consumption. VMI adds our management "
   "of replenishment; DLF (direct line feed) adds our personnel on site filling bins, racks or any "
   "other min/max system. Integrated supply and in-plant store variants extend the same shape. The "
   "defining structure is site schedules and min/max lists changing monthly under a stable master, "
   "settled against consumption reports."),
 tree=[(0,"","","Relationship: PlantCo","rel","",""),
  (1,"","","Consignment / VMI / DLF agreement","master","","on-site labour: DLF only"),
  (2,"forms part of","s","Site schedule per location","comp","",""),
  (2,"forms part of","s","Min/max bin list","comp","supersedes monthly",""),
  (2,"forms part of","s","Replenishment and buy-back terms","comp","",""),
  (2,"evidences","e","Consumption reports","ev","",""),
  (3,"settled by","t","Invoices","ord","","")],
 terms=[("Master","Consignment Agreement; Consignment Stock Agreement; VMI Agreement; Vendor Managed Inventory Agreement; DLF Agreement; Direct Line Feed Agreement; In-Plant Store Agreement; Integrated Supply Agreement; Stocking Agreement"),
  ("Component","Site Schedule; Bin List; Min/Max List; Replenishment Plan; Buy-Back Terms")],
 props="title transfer: on consumption | on-site labour: none, VMI-managed or DLF | site link: covers-site edges into master data",
 complexity=["The min/max list supersedes monthly; treat it as a versioned component or the graph drowns in amendments.",
  "Site schedules carry covers-site edges into master data, which is what makes site-level questions answerable."]),

dict(code="C10", cat="Customers", name="Reseller and sub-distributor",
 test=("The customer resells onward. Territory and product schedules constrain the appointment, and vendor "
   "end-user terms flow down through us into the customer's tree, which creates deliberate edges from "
   "S1 shared nodes into this family."),
 tree=[(0,"","","Relationship: DealerCo","rel","",""),
  (1,"","","Reseller agreement","master","",""),
  (2,"forms part of","s","Territory and product schedules","comp","",""),
  (2,"incorporates","s","Vendor end-user terms","sh","flows down from S1",""),
  (2,"placed under","t","POs","ord","","")],
 terms=[("Master","Reseller Agreement; Dealer Agreement; Sub-Distribution Agreement; Sub-Distributor Agreement; Partner Agreement; Channel Agreement")],
 props="appointment: yes (by us) | territory and product constraints: schedule level | flow-down source: S1 family",
 complexity=["The flows-down-to edges from vendor terms are cross-category and cross-relationship; they are exactly what a folder structure cannot show."]),

dict(code="C11", cat="Customers", name="Public sector frameworks",
 test=("An awarded framework that is not itself a contract to supply; each authority's call-off is. "
   "Authorities fan out under the framework like LPAs under a master. Lots and call-offs are "
   "UK-flavoured terminology; the structure travels across jurisdictions even where the names do not, "
   "so jurisdiction is a property, and OCDS is available as an optional adapter."),
 tree=[(0,"","","Relationship: Authority framework","rel","","jurisdiction: UK"),
  (1,"","","Framework agreement","master","",""),
  (2,"forms part of","s","Lot 2","comp","",""),
  (3,"called off under","s","Call-off contract, authority A","master","",""),
  (4,"placed under","t","Order form","wk","",""),
  (5,"placed under","t","POs","ord","",""),
  (3,"called off under","s","Call-off contract, authority B","master","","")],
 terms=[("Master","Framework Agreement; Dynamic Purchasing System; DPS; Panel Arrangement; Standing Offer; IDIQ (US flavour)"),
  ("Call-off","Call-off Contract; Order Contract; Mini-Competition Award; Task Order; Standing Offer Call-up")],
 props="jurisdiction: ISO 3166 | lot structure: yes or no | call-off basis: direct award or mini-competition",
 complexity=["The framework alone creates no supply obligation; agents must not treat it as a governing master for orders that lack a call-off.",
  "Each calling-off authority is a distinct legal entity with its own party edges into master data."]),

dict(code="C12", cat="Customers", name="E-commerce accounts",
 test=("A registered web account governed by webshop terms, standard or negotiated; users attach to the "
   "account and orders attach through it. Distinct from EDI, API and PunchOut, which are channels "
   "usually documented as a schedule inside another family (overlay O5) because an underlying contract "
   "is typically negotiated. Agent-based ordering is a reserved future channel type."),
 tree=[(0,"","","Relationship: WebBuyerCo","rel","",""),
  (1,"","","E-commerce account","master","","master data link"),
  (2,"governed by","s","Webshop terms v2026","sh","or negotiated agreement",""),
  (2,"attached to","e","Users (authorised buyers)","ev","",""),
  (2,"placed under","t","Web orders","ord","","")],
 terms=[("Anchor","E-commerce Account; Web Account; Online Trade Account; Customer Portal Account"),
  ("Shared terms","Website Terms; Webshop Terms; Online Terms of Sale; E-commerce Terms and Conditions")],
 props="terms: standard or negotiated | users: person nodes with user-of edges | channel overlays: O5 where EDI, API or PunchOut added",
 complexity=["Click-accept is the execution event; capture date and version matter more than signature.",
  "Thousands of accounts share one terms node, the same many-to-one shape as C4."]),

dict(code="C13", cat="Customers", name="Programmes and pricing letters",
 test=("Annual or project-specific commercial letters that vary pricing under whatever else governs: "
   "rebates, growth incentives, special pricing letters. Re-issue supersedes; project letters are "
   "time-limited. They attach to the relationship and reference the governing master or price list "
   "where one exists."),
 tree=[(0,"","","Relationship: KeyAccountCo","rel","",""),
  (1,"","","Rebate letter 2026","ch","supersedes 2025",""),
  (2,"forms part of","s","Targets schedule","comp","",""),
  (1,"","","Growth incentive letter","ch","",""),
  (1,"","","Special pricing letter, project X","ch","varies price list","time-limited")],
 terms=[("Change","Rebate Letter; Rebate Agreement; Growth Incentive Letter; Special Pricing Letter; Pricing Letter; SPA (customer-side sense); Project Pricing Letter")],
 props="cycle: annual re-issue or project | time-limited: usually yes | varies: master or price list",
 complexity=["Annual re-issue makes the supersedes chain the family's backbone; the current letter is a point-in-time query, not a folder.",
  "SPA collides with the supplier-side S9 sense and with Sale and Purchase Agreement; the alias registry disambiguates by category."]),

# ---------------- SUPPLIERS ----------------
dict(code="S1", cat="Suppliers", name="Authorised distribution and channel programmes",
 test=("Appointment is yes: the agreement confers channel status and generates programme children such as "
   "price protection, stock rotation, ship-and-debit and SPA eligibility, often through annual "
   "programme terms that re-issue each year and instruments that bind by notice rather than "
   "signature. The absence of those children is what sends a document to S2 instead."),
 tree=[(0,"","","Relationship: VendorCo","rel","",""),
  (1,"","","Distribution agreement 2018","master","","appointment: yes"),
  (2,"forms part of","s","Territory schedule","comp","",""),
  (2,"forms part of","s","Product schedule","comp","","updated by notice"),
  (2,"forms part of","s","Price list","comp","supersedes by notice",""),
  (2,"forms part of","s","Programme terms 2026","comp","supersedes 2025",""),
  (3,"forms part of","s","Price protection, stock rotation, S&D terms","comp","",""),
  (2,"incorporates","s","End-user terms","sh","flows down to C10",""),
  (2,"amends","l","Amendment 1","ch","",""),
  (2,"placed under","t","Our POs to vendor","ord","","")],
 terms=[("Master","Distribution Agreement; Authorised Distributor Agreement; Master Distributor Agreement; Channel Partner Agreement; Dealer Agreement (their paper); Franchised Distributor Agreement"),
  ("Programme","Programme Terms; Partner Programme Guide; Channel Programme Terms; Price Protection Terms; Stock Rotation Policy; Ship-and-Debit Terms; POS Reporting Requirements")],
 props="appointment: yes | update mechanism: by notice for lists, signature for the master | node status: notified where bound by notice",
 complexity=["Instruments that bind by notice are still nodes, with status notified rather than signed.",
  "Annual programme terms re-issue wholesale; the supersedes chain carries the years.",
  "End-user terms flow down into C10, the family's signature cross-category edge."]),

dict(code="S2", cat="Suppliers", name="Master supply or purchase, no appointment",
 test=("Buy-side relationship terms without channel status. Structurally a mirror of C2. The defining "
   "feature is the absence of programme children: no price protection, no stock rotation, no "
   "ship-and-debit eligibility."),
 tree=[(0,"","","Relationship: MakerCo","rel","",""),
  (1,"","","Master purchase agreement","master","","appointment: no"),
  (2,"forms part of","s","Pricing exhibit","comp","",""),
  (2,"forms part of","s","Quality and delivery terms","comp","",""),
  (2,"placed under","t","Our POs","ord","","")],
 terms=[("Master","Master Purchase Agreement; Master Supply Agreement (their label); Purchase Agreement; Supply Agreement; Goods Supply Agreement")],
 props="appointment: no | commercial completeness: usually no",
 complexity=["The classifier's test against S1 is appointment plus programme children, never the title on the cover."]),

dict(code="S3", cat="Suppliers", name="Framework purchase with releases",
 test=("Buy-side framework with a versioned commercial layer; blanket POs or scheduling agreements sit "
   "between framework and delivery, drawn down by releases. Forecasts hover at the edge of "
   "bindingness and are recorded as evidence with a commitment band, not as orders."),
 tree=[(0,"","","Relationship: MillCo","rel","",""),
  (1,"","","Supply agreement","master","","complete: yes"),
  (2,"forms part of","s","Price list vN","comp","supersedes vN-1",""),
  (2,"forms part of","s","Volume commitment","comp","",""),
  (2,"evidences","e","Rolling forecast","ev","","non-binding band"),
  (2,"placed under","t","Blanket PO / scheduling agreement","ord","",""),
  (3,"released under","t","Releases","ord","","")],
 terms=[("Master","Supply Agreement; LTA; Long-Term Agreement; Framework Purchase Agreement"),
  ("Order","Blanket PO; Blanket Order; Scheduling Agreement; Release; Delivery Schedule; Firm Zone / Trade-off Zone Schedule")],
 props="commercial completeness: yes | forecast: binding band property | commitment: volume",
 complexity=["Forecast versus commitment is the family's recurring dispute; the binding band lives as a property on the forecast evidence node."]),

dict(code="S4", cat="Suppliers", name="Software and cloud partner programmes, for resale",
 test=("Click-through partner stacks for products we resell. Nearly everything incorporated by URL and "
   "updated quarterly; the portal acceptance is the execution event. Strictly for resale: anything "
   "consumed internally is V1 or V2, never this family."),
 tree=[(0,"","","Relationship: CloudVendorCo","rel","","for resale"),
  (1,"","","Partner agreement v2026","master","supersedes v2025",""),
  (2,"incorporates","s","Programme guide (URL)","sh","",""),
  (2,"incorporates","s","Product and regional terms (URL)","sh","",""),
  (2,"forms part of","s","DPA","comp","",""),
  (2,"placed under","t","Portal orders","ord","resold under C-side","")],
 terms=[("Master","Partner Agreement; Cloud Solution Provider Agreement; CSP Agreement; Marketplace Programme Agreement; Reseller Programme Terms; Distribution Partner Terms"),
  ("Shared terms","Programme Guide; Product Terms; Service Terms; Regional Terms; Online Services Terms")],
 props="paper: theirs, click-through | update cadence: quarterly typical | execution event: portal acceptance | purpose: resale only",
 complexity=["Version capture on every incorporates edge is the whole game; the terms you accepted are not the terms on the website today.",
  "Portal orders resold onward create back-to-back edges into customer families."]),

dict(code="S5", cat="Suppliers", name="Commercial agency",
 test=("Agency proper: we act as agent, title never passes, and statutory regimes bite, notably the EU "
   "Commercial Agents Directive and Middle East agency protections with their termination "
   "compensation and registration rules. Kept apart from S6 because the statutory regime changes the "
   "risk profile of the whole family."),
 tree=[(0,"","","Relationship: PrincipalCo","rel","",""),
  (1,"","","Agency agreement","master","","statutory regime: yes"),
  (2,"forms part of","s","Territory and product schedules","comp","",""),
  (2,"forms part of","s","Commission schedule","comp","",""),
  (2,"amends","l","Amendments","ch","","")],
 terms=[("Master","Agency Agreement; Commercial Agency Agreement; Sales Agency Agreement; Sales Representative Agreement (check substance)")],
 props="statutory regime: EU CAD, Middle East agency law, other, none | title: never passes | registration: jurisdiction dependent",
 complexity=["Termination is the event that matters; compensation and indemnity claims arise by statute regardless of the drafting."]),

dict(code="S6", cat="Suppliers", name="Commission and introducer agreements",
 test=("A fee for winning or introducing business, one-off or ongoing, often bringing local knowledge or "
   "project expertise. No statutory agency regime, which is exactly why it is split from S5. Claims "
   "reference the project or customer that earned them, another quiet cross-category edge."),
 tree=[(0,"","","Relationship: IntroducerCo","rel","",""),
  (1,"","","Introducer agreement","master","","regime: none"),
  (2,"forms part of","s","Project scope, commission terms","comp","",""),
  (2,"claimed under","t","Commission claims","ord","references project / customer","")],
 terms=[("Master","Introducer Agreement; Commission Agreement; Finder's Fee Agreement; Referral Agreement; Business Development Agreement")],
 props="regime: none | duration: one-off or ongoing | anti-bribery diligence: flag",
 complexity=["The compliance risk is ABC-shaped, not agency-shaped; diligence evidence attaches through S12-style evidence nodes."]),

dict(code="S7", cat="Suppliers", name="Manufacturing and private label",
 test=("They make to our specification or under our brand. Specifications sit under change control and "
   "version faster than the master; the quality agreement is owned by a different function; tooling "
   "has its own title and lifecycle; a brand licence rides along where private label applies."),
 tree=[(0,"","","Relationship: FactoryCo","rel","",""),
  (1,"","","Manufacturing and supply agreement","master","",""),
  (2,"forms part of","s","Specifications vN","comp","change control",""),
  (2,"forms part of","s","Quality agreement","comp","","owner: quality"),
  (2,"forms part of","s","Tooling agreement","comp","","title: ours"),
  (2,"forms part of","s","Brand licence","comp","",""),
  (2,"placed under","t","Our POs","ord","","")],
 terms=[("Master","Manufacturing and Supply Agreement; Contract Manufacturing Agreement; OEM Supply Agreement; Private Label Agreement; Toll Manufacturing Agreement"),
  ("Component","Specification; Technical Agreement; Quality Agreement; QAA; Tooling Agreement; Brand Licence; Trademark Licence")],
 props="spec control: change control process | tooling title: ours or theirs | brand licence: yes where private label",
 complexity=["Three sub-documents with three different owners (commercial, quality, brand) under one master; ownership is a property worth recording."]),

dict(code="S8", cat="Suppliers", name="Terms of purchase and supplier account forms",
 test=("Mirror of C4 on the buy side. Our terms of purchase govern by default; the supplier's account "
   "form or acknowledgement tries to bind us into theirs, and the conflict is recorded per order with "
   "a last-shot property, never assumed at relationship level."),
 tree=[(0,"","","Relationship: PartsCo","rel","",""),
  (1,"governed by","s","Our terms of purchase vN","sh","",""),
  (2,"placed under","t","Our PO","ord","",""),
  (3,"responds to","t","Their acknowledgement / quote","ord","conflicts with ToP",""),
  (1,"rival instrument","","Their supplier account form","master","conflicts with ToP","")],
 terms=[("Shared terms","Terms of Purchase; Conditions of Purchase; General Purchasing Conditions; Standard Terms of Purchase"),
  ("Rival anchor","Supplier Account Form; New Supplier Form; Vendor Setup Form; Trading Terms Letter")],
 props="last shot: per order | rival anchor present: yes or no",
 complexity=["Their quote often fires first and our PO answers it, reversing the C4 sequence; direction of the responds-to edge captures which."]),

dict(code="S9", cat="Suppliers", name="Special pricing and programme claims",
 test=("High-volume, short-lived commercial instruments tied to a specific customer, project or product: "
   "SPAs, deviated pricing, ship-and-debit, price protection, stock rotation, MDF and co-op, rebates. "
   "Each links to the supplier relationship and to the specific customer relationship it serves, which "
   "makes this the first family whose edges routinely cross categories. DPA here means deviated "
   "pricing agreement, a collision with data processing that the alias registry disambiguates."),
 tree=[(0,"","","Relationship: VendorCo","rel","",""),
  (1,"","","SPA, customer Y, project X","ch","references C-relationship Y","time-limited"),
  (2,"extends","l","Extension letter","ch","",""),
  (1,"claimed under","t","Ship-and-debit claims","ord","",""),
  (1,"claimed under","t","Price protection claims","ord","",""),
  (1,"claimed under","t","MDF / co-op claims","ord","","")],
 terms=[("Change","SPA; Special Pricing Agreement; Deviated Pricing Agreement; DPA (deviated pricing sense); Meet-Comp; Contract Pricing Letter; Project Registration; Design Registration"),
  ("Claims","Ship-and-Debit Claim; S&D Claim; Debit Memo; Price Protection Claim; Stock Rotation Return; MDF Claim; Co-op Claim; Rebate Claim")],
 props="time-limited: yes | linked customer: relationship reference mandatory | claim settlement: credit or debit memo",
 complexity=["Volume is the challenge: thousands of short-lived nodes; the cross edges to customer relationships are the analytical payoff.",
  "Every claim is a transaction node claimed under its instrument, which is what makes margin-recovery questions walkable."]),

dict(code="S10", cat="Suppliers", name="Services for resale, back-to-back",
 test=("Subcontracted services we resell. Supplier SOWs mirror customer SOWs, and the mismatches between "
   "them (warranty period, liability cap, response times) are recorded as gap edges. The mirror and "
   "gap edges into C6 are the family's purpose."),
 tree=[(0,"","","Relationship: SubcontractorCo","rel","",""),
  (1,"","","Services partner agreement","master","",""),
  (2,"forms part of","s","SLA, rate card","comp","",""),
  (2,"agreed under","s","SOW (back-to-back)","wk","mirrors C6 SOW, gap: warranty",""),
  (3,"placed under","t","Work orders","ord","","")],
 terms=[("Master","Services Partner Agreement; Subcontract; Support Reseller Agreement; Installation Subcontract; Field Services Agreement")],
 props="mirror target: C6 SOW reference | gap register: per-term gap edges",
 complexity=["Each material term mismatch is one gap edge with the delta as a property; the set of gap edges is the risk register."]),

dict(code="S11", cat="Suppliers", name="Supplier consignment and drop-ship",
 test=("Their stock in our warehouse with title passing on our draw, or their delivery direct to our "
   "customer. The physical flow bypasses us in drop-ship while the contract flow does not, and the "
   "graph must keep the two apart."),
 tree=[(0,"","","Relationship: StockCo","rel","",""),
  (1,"","","Consignment stock agreement","master","","title: theirs until draw"),
  (2,"forms part of","s","Stock schedule, settlement terms","comp","",""),
  (2,"evidences","e","Consumption reports","ev","",""),
  (1,"varies","l","Drop-ship addendum","ch","delivery direct to C-side","")],
 terms=[("Master","Consignment Stock Agreement; Vendor Consignment Agreement; Bonded Stock Agreement; Drop-Ship Agreement; Direct Ship Addendum")],
 props="title: theirs until draw | physical flow: through us or direct | settlement: on consumption",
 complexity=["Drop-ship creates delivery edges to customer sites while invoicing edges stay with us; conflating the two flows is the classic modelling error."]),

dict(code="S12", cat="Suppliers", name="Quality and compliance evidence",
 test=("Mostly evidence with validity periods rather than contracts: quality agreements aside, this is "
   "declarations of conformity, REACH, RoHS and conflict minerals declarations, certificates of "
   "conformity per batch, insurance certificates. Evidence attaches to products as well as to the "
   "relationship and feeds importer and distributor obligations under product regulation."),
 tree=[(0,"","","Relationship: (any supplier)","rel","",""),
  (1,"","","Quality agreement","master","",""),
  (1,"","","Code of conduct (ours, imposed)","master","",""),
  (1,"evidences","e","DoC, CoC per batch","ev","attaches to product nodes",""),
  (1,"evidences","e","REACH, RoHS, conflict minerals declarations","ev","",""),
  (1,"evidences","e","Insurance certificates","ev","","validity window")],
 terms=[("Evidence","Declaration of Conformity; DoC; Certificate of Conformity; CoC; REACH Declaration; RoHS Declaration; CMRT; Conflict Minerals Report; Certificate of Insurance; COI; Test Report; Mill Certificate")],
 props="validity window: mandatory | attaches to: relationship and product | regulatory driver: importer or distributor obligations",
 complexity=["Batch-level certificates attach to product nodes and even lots; expiry queries are the operational use case."]),

# ---------------- VENDORS ----------------
dict(code="V1", cat="Vendors", name="SaaS subscriptions",
 test=("Own-consumption cloud software. The operative commercial instrument is the order form; the master "
   "sits above it by URL reference and can change; the negotiated security addendum prevails over the "
   "URL terms. Renewal order forms supersede their predecessors."),
 tree=[(0,"","","Relationship: SaaSCo","rel","",""),
  (1,"","","MSA (URL) v2026","sh","mutable master",""),
  (2,"placed under","t","Order form 2","wk","renewal, supersedes OF1",""),
  (2,"forms part of","s","DPA + SCCs","comp","","subprocessors: URL"),
  (2,"incorporates","s","SLA, support, AUP (URL)","sh","",""),
  (2,"forms part of","s","Security addendum (signed)","comp","prevails over URL terms","")],
 terms=[("Master","MSA; Master Subscription Agreement; Cloud Services Agreement; Terms of Service; ToS; Online Services Agreement"),
  ("Work instrument","Order Form; Order Schedule; Subscription Order; Quote (executed)")],
 props="master: by URL, mutable, capture dates mandatory | operative instrument: order form | precedence: signed addendum over URL terms",
 complexity=["Every URL incorporation carries version and capture date; the subprocessor list changes on notice and needs its own capture trail."]),

dict(code="V2", cat="Vendors", name="Enterprise licence and support",
 test=("Perpetual or term licences with annual support renewals forming a chain of new instruments, plus "
   "audit and true-up letters that amend the licensed position."),
 tree=[(0,"","","Relationship: SoftwareCo","rel","",""),
  (1,"","","Licence agreement","master","",""),
  (2,"forms part of","s","Licence schedules","comp","",""),
  (2,"renews under","t","Annual support renewal 2026","wk","chain: 2024, 2025",""),
  (2,"amends","l","True-up letter","ch","","")],
 terms=[("Master","Licence Agreement; Software Licence Agreement; EULA; Volume Licensing Agreement; Enterprise Agreement"),
  ("Renewal","Support Renewal; Maintenance Renewal; Support and Maintenance Order; True-Up Order")],
 props="renewals: new instruments in a chain | true-ups: amendments | audit rights: flag",
 complexity=["Renewals are instruments, not status flips; the chain answers what was supported when."]),

dict(code="V3", cat="Vendors", name="IT services and outsourcing",
 test=("Long-term managed services: master, many SOWs with independent lifecycles, service levels, exit "
   "plan, formal change control producing change notes."),
 tree=[(0,"","","Relationship: MSPCo","rel","",""),
  (1,"","","Services MSA","master","",""),
  (2,"agreed under","s","SOW 1, SOW 2","wk","","independent lifecycles"),
  (3,"amends","l","Change notes","ch","",""),
  (2,"forms part of","s","Service levels, exit plan","comp","","")],
 terms=[("Master","Managed Services Agreement; IT Services Agreement; Outsourcing Agreement; Master Services Agreement"),
  ("Change","Change Note; Change Request; CR; Change Control Note; Contract Change Note")],
 props="exit plan: component with its own review cycle | SOW precedence: per SOW",
 complexity=["Exit is the family's tail risk; the exit plan node and its currency deserve monitoring edges."]),

dict(code="V4", cat="Vendors", name="Telecoms and connectivity",
 test=("A master with hundreds of small service orders per site or circuit, each with its own minimum "
   "term and auto-renewal. The population of orders, not the master, is where the money and the "
   "notice deadlines live."),
 tree=[(0,"","","Relationship: TelcoCo","rel","",""),
  (1,"","","Master services agreement","master","",""),
  (2,"placed under","t","Service orders per site / circuit","wk","","auto-renew, min terms")],
 terms=[("Work instrument","Service Order; Circuit Order; Connection Order; Site Order")],
 props="auto-renew: per order | minimum term: per order | notice window: per order",
 complexity=["Renewal-notice queries run across the order population; the master is almost never the answer."]),

dict(code="V5", cat="Vendors", name="Professional advisers",
 test=("Panel terms or outside counsel guidelines on our paper prevailing over the adviser's terms of "
   "business, with an engagement letter per matter and fee letters varying it. The adviser's own "
   "terms are incorporated and periodically updated."),
 tree=[(0,"","","Relationship: LawFirmLLP","rel","",""),
  (1,"","","Panel terms / outside counsel guidelines","master","prevail over their ToB",""),
  (2,"incorporates","s","Their terms of business vN","sh","",""),
  (2,"engaged under","s","Engagement letter per matter","wk","",""),
  (3,"varies","l","Fee letters, scope changes","ch","","")],
 terms=[("Master","Panel Agreement; Panel Terms; Outside Counsel Guidelines; OCG; Framework Engagement Terms"),
  ("Work instrument","Engagement Letter; Letter of Engagement; Retainer Letter; Terms of Engagement; Matter Confirmation")],
 props="precedence: our guidelines over their ToB | granularity: one engagement per matter",
 complexity=["Matter-level engagement letters map one-to-one onto matters in practice management, a natural join to a different master data set."]),

dict(code="V6", cat="Vendors", name="Recruitment, staffing and contractors",
 test=("Agency terms of business with assignment schedules, consultancy agreements with SOWs, employer of "
   "record arrangements with country addenda. Introduction fees and off-payroll status are the "
   "recurring properties. Employment contracts are out of scope, a people category to decide "
   "separately."),
 tree=[(0,"","","Relationship: AgencyCo","rel","",""),
  (1,"","","Agency terms of business","master","",""),
  (2,"placed under","t","Assignment schedules","wk","",""),
  (1,"","","Consultancy agreement","master","",""),
  (2,"agreed under","s","SOWs","wk","","off-payroll status")],
 terms=[("Master","Terms of Business; ToB; Recruitment Agency Terms; Consultancy Agreement; Contractor Agreement; Employer of Record Agreement; Umbrella Company Terms"),
  ("Work instrument","Assignment Schedule; Placement Confirmation; Assignment Confirmation; SOW")],
 props="introduction fee: window and amount | off-payroll: status per engagement",
 complexity=["Assignment schedules carry person references, joining contract data to people data with the obvious privacy overlay."]),

dict(code="V7", cat="Vendors", name="Property",
 test=("Agreement for lease into lease, then a long life of deeds and consents: rent deposit deed, "
   "licences to alter, assign or sublet, deeds of variation, personal side letters, rent review "
   "memoranda, break notices, subleases. Deeds, statutory overlay and decade-scale lifecycles make "
   "this the slowest family in the graph."),
 tree=[(0,"","","Relationship: LandlordCo","rel","",""),
  (1,"","","Agreement for lease","master","",""),
  (2,"granted under","s","Lease","master","","deed, long life"),
  (3,"forms part of","s","Rent deposit deed","comp","",""),
  (3,"consented under","s","Licences to alter / assign / sublet","comp","",""),
  (3,"varies","l","Deed of variation, side letter","ch","","side letter: personal"),
  (3,"evidences","e","Rent review memorandum","ev","",""),
  (3,"terminates","l","Break notice","ch","",""),
  (3,"granted under","s","Sublease","master","","")],
 terms=[("Master","Agreement for Lease; AfL; Lease; Underlease; Sublease; Licence to Occupy; Reversionary Lease; Wayleave; Heads of Terms (pre-contract)"),
  ("Change","Deed of Variation; Side Letter; Rent Review Memorandum; Licence to Alter; Licence to Assign; Break Notice")],
 props="instrument form: deed | side letters: personal, non-transferable flag | statutory overlay: jurisdiction",
 complexity=["Personal side letters do not bind successors; the personal flag changes what a due diligence walk may rely on."]),

dict(code="V8", cat="Vendors", name="Facilities and equipment",
 test=("Master hire or lease with equipment schedules per asset, acceptance certificates, extensions and "
   "returns, plus FM contracts with site schedules and SLAs. The master-plus-schedules shape is the "
   "C1 pattern wearing overalls."),
 tree=[(0,"","","Relationship: HireCo","rel","",""),
  (1,"","","Master lease / hire agreement","master","",""),
  (2,"placed under","t","Equipment schedule per asset","wk","",""),
  (3,"evidences","e","Acceptance certificate","ev","",""),
  (3,"extends","l","Extension / return note","ch","",""),
  (2,"forms part of","s","FM site schedules, SLAs","comp","","")],
 terms=[("Master","Master Lease; Master Hire Agreement; Equipment Lease; Hire Purchase Agreement; FM Contract; Facilities Management Agreement"),
  ("Work instrument","Equipment Schedule; Asset Schedule; Hire Schedule")],
 props="per-asset schedules: one node per asset | acceptance: evidence gate for payment",
 complexity=["Asset schedules join to fixed-asset registers, another master data set outside this spine but linkable by the same discipline."]),

dict(code="V9", cat="Vendors", name="Logistics and fleet",
 test=("Logistics services agreements with versioned rate cards, lane and site schedules, KPI schedules "
   "and annual rate letters; carrier agreements incorporating standard carrier conditions with their "
   "own liability limits; customs brokerage; fleet master leases. Borderline by design: the cost is "
   "recharged to customers but the service is consumed by us, so vendor."),
 tree=[(0,"","","Relationship: 3PLCo","rel","","cost recharged, service consumed by us"),
  (1,"","","Logistics services agreement","master","",""),
  (2,"forms part of","s","Rate card vN, lane and site schedules","comp","supersedes annually",""),
  (2,"incorporates","s","Standard carrier conditions","sh","","own liability limits"),
  (2,"varies","l","Annual rate letters","ch","","")],
 terms=[("Master","Logistics Services Agreement; 3PL Agreement; Warehousing Agreement; Carriage Agreement; Freight Agreement; Customs Brokerage Agreement; Fleet Lease"),
  ("Shared terms","RHA Conditions; BIFA Conditions; CMR; standard carrier conditions generally")],
 props="incorporated conditions: liability limits recorded | rate cycle: annual",
 complexity=["Incorporated carrier conditions cap liability far below cargo value; the limit belongs on the incorporates edge where an agent will trip over it."]),

dict(code="V10", cat="Vendors", name="Banking, finance and insurance",
 test=("Facility agreements with security documents cutting across group entities, compliance "
   "certificates, amendments and waivers; insurance policies with schedules, endorsements and "
   "renewals; credit insurance whose buyer limits point at customer master data, a deliberate "
   "cross-category edge. Lumped as one family for now; splitting finance from insurance is a known "
   "candidate refinement."),
 tree=[(0,"","","Relationship: BankCo / InsurerCo","rel","",""),
  (1,"","","Facility agreement","master","",""),
  (2,"secured by","s","Debenture, charges","sec","cross group entities",""),
  (2,"evidences","e","Compliance certificates","ev","",""),
  (2,"amends","l","Amendments and waivers","ch","",""),
  (1,"","","Insurance policy","master","",""),
  (2,"forms part of","s","Schedule","comp","",""),
  (2,"amends","l","Endorsements, renewals","ch","",""),
  (2,"forms part of","s","Credit insurance buyer limits","comp","points at customer master data","")],
 terms=[("Master","Facility Agreement; RCF; Revolving Credit Facility; Invoice Finance Agreement; ISDA Master Agreement; Insurance Policy; Credit Insurance Policy"),
  ("Security","Debenture; Charge; Guarantee; Intercreditor Agreement; Security Agreement"),
  ("Change","Amendment and Waiver; Endorsement; Renewal Schedule")],
 props="security scope: entities charged | buyer limits: per customer account | covenant evidence: certificate cycle",
 complexity=["Security documents bind entities that never trade with the counterparty; the party edges are the point.",
  "Credit insurance buyer limits are vendor-category nodes pointing at customer accounts, the graph's most useful cross-category edge for credit control."]),

dict(code="V11", cat="Vendors", name="Indirect goods and services",
 test=("The long tail: terms of purchase, PO, invoice, mostly auto-renewing, individually small and "
   "collectively noisy. Marketing agencies, sponsorships, memberships, data subscriptions, travel, "
   "utilities. Low modelling depth by design: invariant edges, dates and renewal flags."),
 tree=[(0,"","","Relationship: (misc vendors)","rel","",""),
  (1,"governed by","s","Terms of purchase vN","sh","",""),
  (2,"placed under","t","PO","ord","",""),
  (3,"settled by","t","Invoice","ord","","auto-renew, high volume")],
 terms=[("Master","Terms of Purchase; Order Form; Subscription Agreement; Membership Terms; Sponsorship Agreement; Media Buying Terms")],
 props="modelling depth: minimal | renewal: auto flags and dates",
 complexity=["The catch-all discipline matters most here: function tags and invariant edges even where family confidence is low."]),
]

OVERLAYS = [
dict(code="O1", name="Security",
 desc=("Instruments that secure obligations arising anywhere in the graph. Guarantees (parent, bank, "
   "personal), promissory notes and post-dated cheques (Middle East practice), letters of credit by "
   "type (sight, usance, standby, confirmed), bonds (performance, advance payment, retention), "
   "charges. Each has its own lifecycle (expiry, release, calls) and party edges into master data, "
   "because the guarantor is rarely the account holder."),
 nodes="Guarantee; Promissory Note; Post-Dated Cheque; Letter of Credit; Bond; Charge; Debenture",
 edges="secures -> obligations or agreements in any family; party edges -> guarantor legal entity in master data"),
dict(code="O2", name="Dispute resolution",
 desc=("Standstill agreements, settlement agreements, Tomlin and consent orders, waiver letters. Rare, "
   "but their extinguishes edges point at obligations elsewhere in the graph, which makes them "
   "disproportionately valuable to model."),
 nodes="Standstill Agreement; Settlement Agreement; Tomlin Order; Consent Order; Waiver Letter",
 edges="extinguishes -> obligations or claims anywhere in the graph; varies -> surviving terms"),
dict(code="O3", name="Pre-contract",
 desc=("NDAs, LOIs and heads of terms, bids and tender submissions, teaming agreements. Carries the "
   "superseded-by-master property, because whether the master supersedes the NDA is a question every "
   "family inherits. oneNDA is the canonical standard-form node here."),
 nodes="NDA (oneNDA canonical); CDA; LOI; Heads of Terms; MOU; Bid; Tender Submission; Teaming Agreement",
 edges="superseded by -> master (property: yes or no); incorporated into -> master"),
dict(code="O4", name="Codes and policies",
 desc=("Customer-imposed supplier codes of conduct pointing at us, and our codes imposed on suppliers. "
   "Sometimes made contractual, often standalone; the contractual flag is the property that matters."),
 nodes="Supplier Code of Conduct (theirs -> us); Code of Conduct (ours -> suppliers); ESG Policy; Anti-Bribery Policy",
 edges="incorporates or references from any family master; contractual: yes or no"),
dict(code="O5", name="Trading channels",
 desc=("EDI, API and PunchOut. Usually a schedule inside another family because an underlying contract "
   "is typically negotiated; occasionally a standalone trading partner agreement. E-commerce accounts "
   "are a family (C12), not this overlay. Agent-based ordering is a reserved future channel type."),
 nodes="EDI Schedule; API Schedule; PunchOut Schedule; Trading Partner Agreement; cXML Agreement",
 edges="forms part of -> governing family master; enables -> transaction layer channel property"),
dict(code="O6", name="Data protection",
 desc=("DPAs, SCCs or IDTA, joint controller terms, transfer assessments. The same node types appear in "
   "every category with the distributor's role flipping between controller and processor. Facts are "
   "typed like any other terms; DPA here means data processing, disambiguated from the S9 sense by "
   "category."),
 nodes="DPA (data processing sense); SCCs; IDTA; Joint Controller Terms; Transfer Risk Assessment",
 edges="forms part of -> any family master; role property: controller, processor, joint")]

# ---------- registries ----------

NODE_TYPES = [
# id, name, layer, definition, examples
("country","Country","0 Reference","ISO 3166 country","DE; NL; GB; US"),
("currency","Currency","0 Reference","ISO 4217 currency","EUR; USD; GBP"),
("incoterm","Incoterm","0 Reference","ICC Incoterms 2020 rule","DAP; EXW; FCA"),
("classification_code","Classification code","0 Reference","Product classification entry","UNSPSC 26121600; ETIM EC000123"),
("identifier_scheme","Identifier scheme","0 Reference","Registry of identifier schemes (ISO 6523 ICDs and others)","LEI; DUNS; GLN; VAT; EORI; national registry"),
("legal_entity","Legal entity","1 Master data","One node per legal person, ours and theirs alike; ours flagged, never a separate model","DistributorCo GmbH; GlobalCo Inc"),
("group","Group","1 Master data","Commercial grouping only (buying group, franchise, global account programme); never legal ownership","EuroBuy buying group"),
("relationship","Relationship","1/2 boundary","Category anchor per counterparty group per category; anchored in master data, used by the agreement layer","GlobalCo customer relationship"),
("account","Account","1 Master data","Trading arrangement: belongs to one of their entities, held with one of our org units","Sold-to account 10001"),
("site","Site","1 Master data","Location with a function: HQ, warehouse, ship-to, consignment location","Munich plant ship-to"),
("product","Product","1 Master data","Our SKU with manufacturer, MPN, GTIN, classification","SKU CBL-001"),
("person","Person","1 Master data","Contacts, signatories, e-commerce users","Anna Weber, signatory"),
("org_unit","Org unit","1 Master data","Our operational structure hanging off our legal entities","DE sales org; group procurement"),
("identifier","Identifier","1 Master data","Scheme plus value claim with source and validity; never a single ID field","LEI 5299...; DUNS 15-048-3782"),
("master","Master-level instrument","2 Agreement","Governs a relationship or a project; top of a family tree","MSA; framework; distribution agreement; lease"),
("participation","Participation","2 Agreement","Per-entity adoption of a master, signed or deemed","LPA; joinder; country addendum"),
("component","Component","2 Agreement","Forms part of a parent instrument but changes on its own lifecycle","pricing schedule; DPA; exhibit"),
("change","Change","2 Agreement","Alters another node: amendment, variation, side letter, change order, pricing letter","Amendment 1; rebate letter"),
("work_instrument","Work instrument","2 Agreement","Scoped engagement under a master","SOW; order form; engagement letter; equipment schedule"),
("shared_terms","Shared / by-reference terms","2 Agreement","One node referenced by many families; often by URL with capture dates","terms of sale; online MSA; carrier conditions"),
("evidence","Evidence","2 Agreement","Non-contractual record with a validity window","acceptance certificate; DoC; COI; consumption report"),
("security","Security","2 Agreement (O1)","Secures obligations; own lifecycle; guarantor party edges","guarantee; LC; bond; charge"),
("clause","Clause","3 Content","Stable-ID unit of a document (eId convention borrowed from Akoma Ntoso)","msa2021#cl_14"),
("term_fact","Term fact","3 Content","Concerto-typed extracted value, bi-temporal","liability_cap = 12 months' charges"),
("obligation","Obligation","3 Content","ODRL-shaped duty, permission or prohibition with obligor and obligee edges","pay within 30 days"),
("order","Order","4 Transaction","PO, call-off, release, blanket, web order","PO 4471"),
("order_response","Order response","4 Transaction","Acknowledgement, confirmation, quote in response","OA 4471-A"),
("invoice","Invoice","4 Transaction","Billing document","INV-2026-118"),
("claim","Claim","4 Transaction","Programme or commercial claim","ship-and-debit claim"),
]

EDGE_TYPES = [
# id,label,kind,from,to,direction_rule,time,notes
("forms_part_of","forms part of","structural","component|change|security","master|participation|work_instrument","child points at parent","valid_from/to","one structural parent per node"),
("accedes_to","accedes to","structural","participation","master","participation points at master","valid_from/to","status signed or deemed on the node"),
("placed_under","placed under","structural","order|work_instrument","master|participation|component|shared_terms","dependent points at governing node","order_date","attach at the lowest governing node"),
("released_under","released under","structural","order","order","release points at blanket","order_date","framework call-off pattern"),
("agreed_under","agreed under","structural","work_instrument","master","SOW points at master","valid_from/to","precedence property per SOW"),
("called_off_under","called off under","structural","master","component|master","call-off contract points at framework or lot","valid_from/to","public sector pattern C11"),
("engaged_under","engaged under","structural","work_instrument","master","engagement letter points at panel terms","valid_from/to","V5"),
("granted_under","granted under","structural","master","master","lease points at agreement for lease; sublease at lease","valid_from/to","V7"),
("governed_by","governed by","structural","master|order|account","shared_terms","dependent points at terms version","valid_from/to","version in force by date"),
("consented_under","consented under","structural","component","master","licence points at lease","valid_from/to","V7 consents"),
("amends","amends","lifecycle","change","master|component|work_instrument|clause","change points at target","effective_from/to","clause-level target preferred"),
("supersedes","supersedes","lifecycle","any versioned","same type","new points at old","effective_from","old node status superseded"),
("varies","varies","lifecycle","change|participation","master|component|clause","varying node points at varied clause","effective_from/to","LPA variations; side letters"),
("extends","extends","lifecycle","change","master|component|work_instrument","letter points at extended node","effective_from/to",""),
("renews","renews","lifecycle","work_instrument|change","master|work_instrument","renewal points at renewed","effective_from/to","automatic renewal is a node property instead"),
("terminates","terminates","lifecycle","change","master|work_instrument","notice points at terminated node","effective_date","node status change plus edge"),
("novated_to","novated to","lifecycle","master","legal_entity","contract points at incoming entity","effective_date","party edges re-dated, tree untouched"),
("memorialised_in","memorialised in","lifecycle","change","component","exceptions list points at special conditions","effective_date","C8"),
("incorporates","incorporates","reference","master|order","shared_terms|component","incorporating doc points at incorporated","captured_at, version","URL terms need capture dates"),
("prevails_over","prevails over","reference","component|master","shared_terms|component|master","winner points at loser","","order of precedence; must stay acyclic"),
("conflicts_with","conflicts with","reference","order|master","shared_terms|master","later shot points at earlier","order_date","battle of the forms; last_shot property"),
("flows_down_to","flows down to","reference","shared_terms|change","master|participation|relationship","source terms point at receiving tree","valid_from/to","S1 to C10; global amendments to LPAs"),
("mirrors","mirrors","reference","work_instrument","work_instrument","supplier SOW points at customer SOW","","back-to-back S10 to C6"),
("gap","gap","reference","work_instrument|term_fact","work_instrument|term_fact","supplier side points at customer side","","delta stored as property; the risk register"),
("references","references","reference","change|master","relationship|master|order","referring node points at referred","","S9 SPA to customer relationship"),
("secures","secures","reference","security","master|obligation|account","security points at secured thing","valid_from/to","O1"),
("extinguishes","extinguishes","reference","master","obligation|claim","settlement points at extinguished obligation","effective_date","O2"),
("limits","limits","reference","component","account|legal_entity","buyer limit points at customer account","valid_from/to","V10 credit insurance"),
("evidences","evidences","evidence","evidence","master|component|work_instrument|order","evidence points at evidenced node","validity window",""),
("party_to","party to","party","master|participation|work_instrument|security|change","legal_entity","instrument points at signatory entity","valid_from/to","the invariant, half one"),
("guaranteed_by","guaranteed by","party","master|account","legal_entity","secured thing points at guarantor","valid_from/to","O1 party edge"),
("ordered_by","ordered by","transaction","order","account","order points at account","order_date","the invariant, half two"),
("settled_by","settled by","transaction","evidence|order","invoice","settled thing points at invoice","","C9 consumption settlement"),
("claimed_under","claimed under","transaction","claim","change|component","claim points at entitling instrument","claim_date","S9"),
("responds_to","responds to","transaction","order_response|order","order","response points at what it answers","","direction records last shot"),
("covers_product","covers product","masterdata","component|change","product|classification_code","schedule points at covered product","valid_from/to",""),
("covers_territory","covers territory","masterdata","component","country","schedule points at country","valid_from/to",""),
("covers_site","covers site","masterdata","component","site","site schedule points at site","valid_from/to","C9"),
("anchored_to","anchored to","masterdata","relationship","legal_entity","relationship points at top in-scope entity","valid_from/to",""),
("belongs_to","belongs to","masterdata","account","legal_entity","account points at owning counterparty entity","valid_from/to",""),
("held_with","held with","masterdata","account","org_unit","account points at our org unit","valid_from/to",""),
("unit_of","unit of","masterdata","org_unit","legal_entity","org unit points at our entity","valid_from/to",""),
("operated_by","operated by","masterdata","site","legal_entity","site points at operating entity","valid_from/to",""),
("partner_function","partner function","masterdata","account","site|account","account points at functional partner","valid_from/to","function property: sold_to, ship_to, bill_to, payer"),
("made_by","made by","masterdata","product","legal_entity","product points at manufacturer","",""),
("part_xref","part cross-reference","masterdata","account","product","account points at product","valid_from/to","their part number as property"),
("member_of","member of","masterdata","legal_entity","group","entity points at commercial group","valid_from/to","never legal ownership"),
("owns","owns","masterdata","legal_entity","legal_entity","parent points at subsidiary","valid_from/to","GLEIF relationship data where LEIs exist"),
("identified_by","identified by","masterdata","legal_entity|site|product","identifier","thing points at identifier claim","valid_from/to","scheme plus value; source recorded"),
("acts_for","acts for","masterdata","person","legal_entity","person points at entity","valid_from/to","role property: signatory, contact"),
("user_of","user of","masterdata","person","account","person points at account","valid_from/to","C12 users"),
("classified_as","classified as","masterdata","product","classification_code","product points at class","","UNSPSC or ETIM"),
("has_clause","has clause","content","master|participation|component","clause","document points at its clause","","stable eId convention"),
("tagged_as","tagged as","content","clause|master","identifier_scheme","clause points at SALI IRI","","vocabulary edge"),
("has_term","has term","content","clause","term_fact","clause points at extracted fact","valid_from/to, recorded_at","bi-temporal"),
("has_obligation","has obligation","content","clause","obligation","clause points at obligation","",""),
("obligor","obligor","content","obligation","legal_entity","obligation points at who owes it","","reinforces the invariant"),
("obligee","obligee","content","obligation","legal_entity","obligation points at who is owed","",""),
("cross_refers_to","cross-refers to","content","clause","clause","referring clause points at referred","","dangling edge = broken cross-reference"),
("defined_in","defined in","content","clause","clause","using clause points at definition","",""),
]

PROPERTIES = [
# property, applies_to, allowed_values, definition
("scope","master","global | regional | single | group_referenced","Whether the master itself contemplates multi-entity adoption; intentionality, not what local entities later do"),
("paper","master|participation","ours | theirs | hybrid | model_form","Whose base document; model_form for NEC, JCT, FIDIC and similar"),
("commercial_completeness","master","yes | no","Whether an order alone completes a contract on pre-agreed commercials; the master v framework test"),
("commitment","master","none | volume | target | exclusivity","Binding commercial commitment carried by the master"),
("appointment","master","yes | no","Whether the agreement confers channel status; the S1 v S2 test"),
("status","any document node","signed | deemed | notified | active | superseded | terminated | expired | provisional","Deemed for participation without signature; notified for instruments binding by notice; provisional pending review"),
("flow_down","change|shared_terms","yes | no | per_accession","Whether the instrument reaches participation nodes automatically"),
("jurisdiction","master|relationship","ISO 3166 code","Governing or procurement jurisdiction"),
("governing_law","master|participation|work_instrument","ISO 3166-2 or named system","Extracted governing law"),
("time_limited","change","yes | no","Project letters and SPAs expire by design"),
("statutory_regime","master","eu_cad | me_agency | other | none","S5 v S6 test"),
("precedence","work_instrument|component","free text chain","Order of precedence where it deviates from default"),
("last_shot","order|order_response","ours | theirs | unresolved","Battle of the forms outcome per order"),
("title_transfer","master","on_delivery | on_consumption | on_payment | retained","C9 and S11"),
("captured_at","edge: incorporates|governed_by","date","Capture date of URL-incorporated terms"),
("version","shared_terms|component","free text","Version label of the referenced terms"),
("valid_from","node or edge","date","Start of real-world validity"),
("valid_to","node or edge","date","End of real-world validity"),
("recorded_at","term_fact and audit rows","datetime","When the graph learned it; second time axis"),
("source_system","any node","system id","Lineage: the system of record"),
("source_key","any node","key","Lineage: key in the system of record"),
("confidence","any classified node","0.00 to 1.00","Classifier confidence; drives review queue"),
("function_tag","unclassified document","governs | transacts | changes | secures | evidences | resolves | enables_channel | pre_contract","Catch-all fallback classification; nearly always determinable"),
("is_ours","legal_entity","true | false","Symmetry flag; never a separate schema"),
("partner_function","edge: partner_function","sold_to | ship_to | bill_to | payer | ordering | goods_supplier | invoicing_party | payee","SAP-style functional roles"),
("category","relationship","customer | supplier | vendor","Category is a property of the relationship, not of the legal entity"),
("their_part_no","edge: part_xref","free text","Customer or supplier part number"),
("role","person or acts_for edge","signatory | contact | user | authorised_buyer","What the person does"),
]

STANDARDS = [
# slot, standard, steward, status, what_we_take, adoption_evidence, url
("Clause and document vocabulary","SALI LMSS","SALI Alliance","adopt","IRIs for document types, clause components, player roles; family registry carries matching IRIs","Thomson Reuters, LexisNexis, NetDocuments, iManage; DLA Piper, Clifford Chance; Microsoft, Intel legal departments","https://sali.org"),
("Transaction documents","UBL (ISO/IEC 19845)","OASIS / ISO","adopt","Order, order response, despatch advice, invoice shapes; DocumentReference carries placed-under","Peppol network; EU e-invoicing mandates; shipped by major ERPs","https://docs.oasis-open.org/ubl/"),
("Deal-point schemas","Concerto (Accord Project)","Linux Foundation","adopt","Typed models of expected terms per family; extraction targets that validate structurally","DocuSign Iris maps extractions to Concerto models; supported by DocuSign, IBM","https://accordproject.org"),
("Obligations","ODRL","W3C (Recommendation)","adopt","Duty, permission, prohibition shape with obligor, obligee, constraints","Catena-X policies; Dataspace Protocol; IDSA and Gaia-X specifications","https://www.w3.org/TR/odrl-model/"),
("Standard-form NDA (O3)","oneNDA","oneNDA / Claustack community","adopt_form","Canonical pre-contract node","3,000+ organisations including Coca-Cola, UBS, Panasonic, Revolut; SteerCo incl. Airbus, Barclays, A&O, Freshfields, Linklaters","https://onenda.org"),
("Lifecycle event pattern","FINOS CDM","FINOS / Linux Foundation with ISDA, ICMA, ISLA","pattern","Amendment, novation, termination as typed events producing new states","JPMorgan production use; BNP, BMO, RBC; JSCC first CCP in production","https://cdm.finos.org"),
("Stable clause IDs","Akoma Ntoso eId convention","OASIS LegalDocML","pattern","Naming convention only: doc#cl_n identifiers and hierarchy plus cross-reference model","European Parliament, EU institutions, UN system for legislative documents","https://docs.oasis-open.org/legaldocml/"),
("Extraction benchmark","CUAD","Atticus Project","test_set","Validation set for clause extraction; not part of the standard","De facto benchmark across legal AI extraction research and vendor evals","https://www.atticusprojectai.org/cuad"),
("Public sector adapter (C11)","OCDS","Open Contracting Partnership","optional_adapter","Mapping for authority-side procurement data where relevant","50+ governments; G20 endorsed","https://standard.open-contracting.org"),
("Negotiated-terms research","WorldCC most-negotiated terms","WorldCC","research_input","Priority order for which deal points each family model extracts first","Industry-standard annual study","https://www.worldcc.com"),
("Entity identifiers","LEI (ISO 17442) + GLEIF relationship data","GLEIF","adopt","Entity identifier scheme; open parent-subsidiary graph","Regulatorily mandated in financial reporting; open data","https://www.gleif.org"),
("Location and product identifiers","GS1 GLN and GTIN","GS1","adopt","Site and product identifier schemes","Global retail and logistics backbone","https://www.gs1.org"),
("Product classification","UNSPSC or ETIM","GS1 US / ETIM International","adopt","Classification codes on product nodes","Widely used in distribution and e-procurement","https://www.unspsc.org"),
("Reference data","ISO 3166, 4217, 6523, 8000","ISO","adopt","Countries, currencies, identifier scheme registry, master data quality","Universal","https://www.iso.org"),
("Common commercial identifier","DUNS","Dun & Bradstreet","note","Ubiquitous but proprietary; store as one identifier scheme among several, never the primary key","Universal in credit and supplier onboarding","https://www.dnb.com"),
("Deontic logic","LegalRuleML","OASIS","dropped","Nothing; ODRL covers the need at our depth","Academic adoption only","https://docs.oasis-open.org/legalruleml/"),
("Privacy vocabulary","DPV","W3C community group","dropped","Nothing; O6 facts typed in Concerto like all terms","Community group output, no Recommendation status, no blue-chip adopters identified","https://w3c.github.io/dpv/"),
("Fine-grained clause labels","LEDGAR","academic (LexGLUE)","dropped","Nothing; SALI is the sole clause vocabulary","Academic dataset","https://aclanthology.org"),
("Standard-form agreements","Common Paper, Bonterms","Common Paper Inc / Bonterms","dropped","Design-pattern evidence only: cover page plus standard terms mirrors shared-node plus deal-points","Real users, but startup-published forms rather than standards","https://commonpaper.com"),
]

# ---------- sample graph ----------
# nodes: (id, name, label, layer, props dict)
N = []
def node(i, name, label, layer, **p): N.append((i, name, label, layer, p))

# reference
node("CNT-DE","Germany","Country","0"); node("CNT-NL","Netherlands","Country","0")
node("CNT-GB","United Kingdom","Country","0"); node("CNT-US","United States","Country","0")
node("CUR-EUR","Euro","Currency","0"); node("CUR-USD","US Dollar","Currency","0")
node("CLS-26121600","Electrical cable (UNSPSC 26121600)","ClassificationCode","0")
# our side
node("LE-DH","DistributorCo Holdings Ltd","LegalEntity","1", is_ours="true", jurisdiction="GB")
node("LE-DDE","DistributorCo GmbH","LegalEntity","1", is_ours="true", jurisdiction="DE")
node("LE-DNL","DistributorCo BV","LegalEntity","1", is_ours="true", jurisdiction="NL")
node("OU-DE-SALES","DE sales org","OrgUnit","1", type="sales_org")
node("OU-NL-SALES","NL sales org","OrgUnit","1", type="sales_org")
node("OU-PROC","Group procurement","OrgUnit","1", type="procurement")
node("ID-LEI-DH","LEI LEI-EXAMPLE-0001","Identifier","1", scheme="LEI", value="LEI-EXAMPLE-0001")
# GlobalCo (customer)
node("LE-GINC","GlobalCo Inc","LegalEntity","1", jurisdiction="US")
node("LE-GDE","GlobalCo GmbH","LegalEntity","1", jurisdiction="DE")
node("LE-GNL","GlobalCo BV","LegalEntity","1", jurisdiction="NL")
node("ID-LEI-GINC","LEI LEI-EXAMPLE-0002","Identifier","1", scheme="LEI", value="LEI-EXAMPLE-0002")
node("AC-10001","Account 10001 GlobalCo GmbH","Account","1", currency="EUR", payment_terms="net 45")
node("AC-10002","Account 10002 GlobalCo BV","Account","1", currency="EUR", payment_terms="net 30")
node("ST-MUC","GlobalCo plant Munich","Site","1", function="ship_to", country="DE")
node("PR-ANNA","Anna Weber","Person","1", role="signatory")
node("PD-CBL001","SKU CBL-001 LV cable","Product","1", mpn="VX-90-CBL")
node("RL-C-GLOBALCO","GlobalCo customer relationship","Relationship","1/2", category="customer")
# C1 family docs
node("DOC-MSA-2021","Global MSA 2021","Master","2", family="C1", status="active", scope="global", paper="ours", commercial_completeness="no", governing_law="England", valid_from="2021-03-01")
node("CL-MSA-14","MSA clause 14 cap on liability","Clause","3", eid="msa2021#cl_14", sali_tag="cap_on_liability")
node("CL-MSA-9","MSA clause 9 payment","Clause","3", eid="msa2021#cl_9", sali_tag="payment_terms")
node("TF-CAP-1","liability cap = 12 months' charges","TermFact","3", valid_from="2021-03-01", valid_to="2024-05-31", recorded_at="2026-01-15")
node("TF-CAP-2","liability cap = 24 months' charges","TermFact","3", valid_from="2024-06-01", recorded_at="2026-01-15")
node("OB-PAY30","pay undisputed invoices within 45 days","Obligation","3", modality="duty")
node("DOC-SCH1","Schedule 1 products","Component","2", family="C1", status="active")
node("DOC-SCH2-V2","Schedule 2 pricing v2","Component","2", family="C1", status="superseded", valid_to="2023-12-31")
node("DOC-SCH2-V3","Schedule 2 pricing v3","Component","2", family="C1", status="active", valid_from="2024-01-01")
node("DOC-DPA-2023","Data processing agreement 2023","Component","2", family="C1", status="active")
node("DOC-AMD1-2022","Amendment 1 (2022)","Change","2", family="C1", status="active", effective_from="2024-06-01")
node("DOC-SIDE-2023","Side letter 2023","Change","2", family="C1", status="active", flow_down="per_accession")
node("DOC-LPA-DE","LPA Germany 2021","Participation","2", family="C1", status="signed")
node("DOC-LSCHA","Local schedule A delivery sites","Component","2", family="C1", status="active")
node("DOC-LAMD1","Local amendment 1 (2023)","Change","2", family="C1", status="active")
node("DOC-LPA-NL","LPA Netherlands","Participation","2", family="C1", status="deemed")
node("TX-PO-4471","PO 4471","Order","4", order_date="2026-02-11")
node("TX-PO-9120","PO 9120","Order","4", order_date="2026-06-03")
node("TX-PO-5100","PO 5100","Order","4", order_date="2026-04-19")
# VendorCo (supplier)
node("LE-VINC","VendorCo Inc","LegalEntity","1", jurisdiction="US")
node("AC-20001","Vendor account 20001","Account","1", currency="USD", payment_terms="net 60")
node("RL-S-VENDORCO","VendorCo supplier relationship","Relationship","1/2", category="supplier")
node("DOC-DIST-2018","Distribution agreement 2018","Master","2", family="S1", status="active", appointment="yes", paper="theirs")
node("DOC-TERR","Territory schedule EMEA","Component","2", family="S1", status="active")
node("DOC-PLIST-2025","Vendor price list 2025","Component","2", family="S1", status="superseded", valid_to="2025-12-31")
node("DOC-PLIST-2026","Vendor price list 2026","Component","2", family="S1", status="notified", valid_from="2026-01-01")
node("DOC-PROG-2026","Programme terms 2026","Component","2", family="S1", status="notified")
node("DOC-EUT","Vendor end-user terms","SharedTerms","2", family="S1", status="active", version="2025-09", captured_at="2025-09-14")
node("DOC-SPA-001","SPA customer GlobalCo project Falcon","Change","2", family="S9", status="active", time_limited="yes", valid_from="2026-01-01", valid_to="2026-12-31")
node("TX-SD-0007","Ship-and-debit claim 0007","Claim","4", claim_date="2026-03-02")
node("TX-PO-V-3001","Our PO 3001 to VendorCo","Order","4", order_date="2026-02-20")
# SaaSCo (vendor)
node("LE-SAAS","SaaSCo Ltd","LegalEntity","1", jurisdiction="GB")
node("RL-V-SAASCO","SaaSCo vendor relationship","Relationship","1/2", category="vendor")
node("DOC-SMSA","SaaSCo master (URL) v2026","SharedTerms","2", family="V1", status="active", version="2026-04", captured_at="2026-04-02")
node("DOC-OF1","Order form 1 (2023)","WorkInstrument","2", family="V1", status="superseded", valid_to="2024-08-31")
node("DOC-OF2","Order form 2 (2024 renewal)","WorkInstrument","2", family="V1", status="active", valid_from="2024-09-01")
node("DOC-SDPA","SaaSCo DPA + SCCs","Component","2", family="V1", status="active")
node("DOC-SECADD","Security addendum (signed)","Component","2", family="V1", status="active")

E = []
def edge(a, t, b, **p): E.append((a, t, b, p))

# master data
edge("LE-GINC","OWNS","LE-GDE", valid_from="2015-01-01")
edge("LE-GINC","OWNS","LE-GNL", valid_from="2018-01-01")
edge("LE-DH","OWNS","LE-DDE"); edge("LE-DH","OWNS","LE-DNL")
edge("LE-DH","IDENTIFIED_BY","ID-LEI-DH"); edge("LE-GINC","IDENTIFIED_BY","ID-LEI-GINC")
edge("OU-DE-SALES","UNIT_OF","LE-DDE"); edge("OU-NL-SALES","UNIT_OF","LE-DNL"); edge("OU-PROC","UNIT_OF","LE-DH")
edge("RL-C-GLOBALCO","ANCHORED_TO","LE-GINC"); edge("RL-S-VENDORCO","ANCHORED_TO","LE-VINC"); edge("RL-V-SAASCO","ANCHORED_TO","LE-SAAS")
edge("AC-10001","BELONGS_TO","LE-GDE"); edge("AC-10001","HELD_WITH","OU-DE-SALES")
edge("AC-10002","BELONGS_TO","LE-GNL"); edge("AC-10002","HELD_WITH","OU-NL-SALES")
edge("AC-20001","BELONGS_TO","LE-VINC"); edge("AC-20001","HELD_WITH","OU-PROC")
edge("ST-MUC","OPERATED_BY","LE-GDE")
edge("AC-10001","PARTNER_FUNCTION","ST-MUC", function="ship_to")
edge("PD-CBL001","MADE_BY","LE-VINC"); edge("PD-CBL001","CLASSIFIED_AS","CLS-26121600")
edge("AC-10001","PART_XREF","PD-CBL001", their_part_no="GP-778")
edge("PR-ANNA","ACTS_FOR","LE-GDE", role="signatory")
# C1 agreement layer + invariant
edge("DOC-MSA-2021","PARTY_TO","LE-DH"); edge("DOC-MSA-2021","PARTY_TO","LE-GINC")
edge("DOC-SCH1","FORMS_PART_OF","DOC-MSA-2021")
edge("DOC-SCH2-V2","FORMS_PART_OF","DOC-MSA-2021"); edge("DOC-SCH2-V3","FORMS_PART_OF","DOC-MSA-2021")
edge("DOC-SCH2-V3","SUPERSEDES","DOC-SCH2-V2", effective_from="2024-01-01")
edge("DOC-DPA-2023","FORMS_PART_OF","DOC-MSA-2021")
edge("DOC-AMD1-2022","FORMS_PART_OF","DOC-MSA-2021"); edge("DOC-AMD1-2022","AMENDS","CL-MSA-14", effective_from="2024-06-01")
edge("DOC-SIDE-2023","FORMS_PART_OF","DOC-MSA-2021")
edge("DOC-LPA-DE","ACCEDES_TO","DOC-MSA-2021")
edge("DOC-LPA-DE","PARTY_TO","LE-DDE"); edge("DOC-LPA-DE","PARTY_TO","LE-GDE")
edge("DOC-LSCHA","FORMS_PART_OF","DOC-LPA-DE")
edge("DOC-LAMD1","FORMS_PART_OF","DOC-LPA-DE"); edge("DOC-LAMD1","VARIES","CL-MSA-14")
edge("DOC-LPA-NL","ACCEDES_TO","DOC-MSA-2021")
edge("DOC-LPA-NL","PARTY_TO","LE-DNL"); edge("DOC-LPA-NL","PARTY_TO","LE-GNL")
edge("TX-PO-4471","PLACED_UNDER","DOC-LPA-DE"); edge("TX-PO-4471","ORDERED_BY","AC-10001")
edge("TX-PO-9120","PLACED_UNDER","DOC-LPA-DE"); edge("TX-PO-9120","ORDERED_BY","AC-10001")
edge("TX-PO-5100","PLACED_UNDER","DOC-LPA-NL"); edge("TX-PO-5100","ORDERED_BY","AC-10002")
# content layer
edge("DOC-MSA-2021","HAS_CLAUSE","CL-MSA-14"); edge("DOC-MSA-2021","HAS_CLAUSE","CL-MSA-9")
edge("CL-MSA-14","HAS_TERM","TF-CAP-1"); edge("CL-MSA-14","HAS_TERM","TF-CAP-2")
edge("TF-CAP-2","SUPERSEDES","TF-CAP-1", effective_from="2024-06-01")
edge("CL-MSA-9","HAS_OBLIGATION","OB-PAY30")
edge("OB-PAY30","OBLIGOR","LE-GINC"); edge("OB-PAY30","OBLIGEE","LE-DH")
# S1 / S9
edge("DOC-DIST-2018","PARTY_TO","LE-DH"); edge("DOC-DIST-2018","PARTY_TO","LE-VINC")
edge("DOC-TERR","FORMS_PART_OF","DOC-DIST-2018")
edge("DOC-TERR","COVERS_TERRITORY","CNT-DE"); edge("DOC-TERR","COVERS_TERRITORY","CNT-NL"); edge("DOC-TERR","COVERS_TERRITORY","CNT-GB")
edge("DOC-PLIST-2025","FORMS_PART_OF","DOC-DIST-2018"); edge("DOC-PLIST-2026","FORMS_PART_OF","DOC-DIST-2018")
edge("DOC-PLIST-2026","SUPERSEDES","DOC-PLIST-2025", effective_from="2026-01-01")
edge("DOC-PROG-2026","FORMS_PART_OF","DOC-DIST-2018")
edge("DOC-DIST-2018","INCORPORATES","DOC-EUT", captured_at="2025-09-14", version="2025-09")
edge("DOC-EUT","FLOWS_DOWN_TO","RL-C-GLOBALCO")
edge("DOC-SPA-001","FORMS_PART_OF","DOC-DIST-2018")
edge("DOC-SPA-001","REFERENCES","RL-C-GLOBALCO")
edge("DOC-SPA-001","COVERS_PRODUCT","PD-CBL001")
edge("TX-SD-0007","CLAIMED_UNDER","DOC-SPA-001")
edge("TX-PO-V-3001","PLACED_UNDER","DOC-DIST-2018"); edge("TX-PO-V-3001","ORDERED_BY","AC-20001")
# V1
edge("DOC-OF2","GOVERNED_BY","DOC-SMSA", captured_at="2026-04-02", version="2026-04")
edge("DOC-OF2","PARTY_TO","LE-DH"); edge("DOC-OF2","PARTY_TO","LE-SAAS")
edge("DOC-OF1","GOVERNED_BY","DOC-SMSA")
edge("DOC-OF2","SUPERSEDES","DOC-OF1", effective_from="2024-09-01")
edge("DOC-SDPA","FORMS_PART_OF","DOC-OF2")
edge("DOC-SECADD","FORMS_PART_OF","DOC-OF2")
edge("DOC-SECADD","PREVAILS_OVER","DOC-SMSA")

SAMPLE_NODES, SAMPLE_EDGES = N, E

ALIASES = []
def _al(nt, fam, items, note=""):
    for a in items: ALIASES.append((a, nt, fam, note))
_al("master","C1",["MSA","Master Agreement","Master Supply Agreement","Master Sales Agreement","Global Master Agreement","Global Framework Agreement","Umbrella Agreement","Global Procurement Agreement","Global Terms Agreement"])
_al("participation","C1",["LPA","LIA","PA","MCA","Local Participation Agreement","Local Implementation Agreement","Participation Agreement","Master Country Agreement","Country Addendum","Accession Agreement","Adherence Agreement","Joinder","Affiliate Agreement","Local Country Agreement"])
_al("master","C2",["Supply Agreement","Sales Agreement","Master Purchase Agreement","Vendor Agreement","Procurement Agreement","Trading Agreement","Commercial Agreement","Supplier Agreement"],"their label for us on their paper")
_al("master","C3",["Framework Agreement","Framework Supply Agreement","Pricing Agreement","LTA","Long-Term Agreement","Preferred Supplier Agreement","Blanket Order Agreement"])
_al("master","C4",["CAF","Customer Account Application Form","Account Application","Account Opening Form","Credit Application","Trade Account Form"],"anchor, quasi-framework")
_al("master","C4",["Vendor Registration Form","Supplier Onboarding Form","Supplier Setup Form"],"their rival anchor")
_al("shared_terms","C4",["Terms of Sale","Terms and Conditions of Sale","Conditions of Sale","General Conditions","Standard Terms"])
_al("master","C5",["VAS Agreement","Value-Added Services Schedule","Supply Chain Services Agreement","Kitting Agreement","Cutting Services Schedule","Configuration Services Schedule"])
_al("master","C6",["Services MSA","Master Services Agreement","Professional Services Agreement","Installation Services Agreement"])
_al("work_instrument","C6",["SOW","Statement of Work","Work Order","Service Order","Task Order","Project Order"])
_al("change","C6",["Change Order","Change Control Note","CCN"])
_al("master","C7",["NEC Subcontract","JCT Subcontract","FIDIC Subcontract","Works Order","Project Supply Agreement","Trade Contract"])
_al("change","C7",["Variation Order","Compensation Event","Variation Instruction"])
_al("security","C7",["Performance Bond","Advance Payment Bond","Retention Bond","Collateral Warranty","Parent Company Guarantee"])
_al("change","C8",["Exceptions List","Exceptions and Clarifications","Deviations List","Comments Sheet","Bid Qualifications"])
_al("shared_terms","C8",["General Conditions of Purchase","GC","General Terms and Conditions of Purchase"])
_al("component","C8",["Special Conditions","SC","Particular Conditions","Supplementary Conditions"])
_al("master","C9",["Consignment Agreement","Consignment Stock Agreement","VMI Agreement","Vendor Managed Inventory Agreement","DLF Agreement","Direct Line Feed Agreement","In-Plant Store Agreement","Integrated Supply Agreement","Stocking Agreement"])
_al("master","C10",["Reseller Agreement","Dealer Agreement","Sub-Distribution Agreement","Sub-Distributor Agreement","Partner Agreement","Channel Agreement"])
_al("master","C11",["Dynamic Purchasing System","DPS","Panel Arrangement","Standing Offer","IDIQ"])
_al("master","C11",["Call-off Contract","Order Contract","Mini-Competition Award","Standing Offer Call-up"],"call-off level")
_al("master","C12",["E-commerce Account","Web Account","Online Trade Account","Customer Portal Account"])
_al("shared_terms","C12",["Website Terms","Webshop Terms","Online Terms of Sale","E-commerce Terms and Conditions"])
_al("change","C13",["Rebate Letter","Rebate Agreement","Growth Incentive Letter","Special Pricing Letter","Pricing Letter","Project Pricing Letter"])
_al("master","S1",["Distribution Agreement","Authorised Distributor Agreement","Master Distributor Agreement","Channel Partner Agreement","Franchised Distributor Agreement"])
_al("component","S1",["Programme Terms","Partner Programme Guide","Channel Programme Terms","Price Protection Terms","Stock Rotation Policy","Ship-and-Debit Terms","POS Reporting Requirements"])
_al("master","S2",["Master Purchase Agreement","Goods Supply Agreement","Purchase Agreement"])
_al("order","S3",["Blanket PO","Blanket Order","Scheduling Agreement","Release","Delivery Schedule"])
_al("master","S4",["Partner Agreement","Cloud Solution Provider Agreement","CSP Agreement","Marketplace Programme Agreement","Reseller Programme Terms","Distribution Partner Terms"])
_al("master","S5",["Agency Agreement","Commercial Agency Agreement","Sales Agency Agreement","Sales Representative Agreement"],"check substance for statutory regime")
_al("master","S6",["Introducer Agreement","Commission Agreement","Finder's Fee Agreement","Referral Agreement","Business Development Agreement"])
_al("master","S7",["Manufacturing and Supply Agreement","Contract Manufacturing Agreement","OEM Supply Agreement","Private Label Agreement","Toll Manufacturing Agreement"])
_al("component","S7",["Specification","Technical Agreement","Quality Agreement","QAA","Tooling Agreement","Brand Licence","Trademark Licence"])
_al("shared_terms","S8",["Terms of Purchase","Conditions of Purchase","General Purchasing Conditions","Standard Terms of Purchase"])
_al("master","S8",["Supplier Account Form","New Supplier Form","Vendor Setup Form","Trading Terms Letter"],"their rival anchor")
_al("change","S9",["SPA","Special Pricing Agreement","Deviated Pricing Agreement","DPA","Meet-Comp","Contract Pricing Letter","Project Registration","Design Registration"],"DPA here = deviated pricing; S9 SPA collides with C13 and with Sale and Purchase Agreement; disambiguate by category")
_al("claim","S9",["Ship-and-Debit Claim","S&D Claim","Debit Memo","Price Protection Claim","Stock Rotation Return","MDF Claim","Co-op Claim","Rebate Claim"])
_al("master","S10",["Services Partner Agreement","Subcontract","Support Reseller Agreement","Installation Subcontract","Field Services Agreement"])
_al("master","S11",["Consignment Stock Agreement","Vendor Consignment Agreement","Bonded Stock Agreement","Drop-Ship Agreement","Direct Ship Addendum"])
_al("evidence","S12",["Declaration of Conformity","DoC","Certificate of Conformity","CoC","REACH Declaration","RoHS Declaration","CMRT","Conflict Minerals Report","Certificate of Insurance","COI","Test Report","Mill Certificate"])
_al("shared_terms","V1",["Master Subscription Agreement","Cloud Services Agreement","Terms of Service","ToS","Online Services Agreement"])
_al("work_instrument","V1",["Order Form","Order Schedule","Subscription Order"],"Order Form also appears in C11 and SaaS resale; disambiguate by category")
_al("master","V2",["Licence Agreement","Software Licence Agreement","EULA","Volume Licensing Agreement","Enterprise Agreement"])
_al("master","V3",["Managed Services Agreement","IT Services Agreement","Outsourcing Agreement"])
_al("work_instrument","V4",["Service Order","Circuit Order","Connection Order","Site Order"])
_al("master","V5",["Panel Agreement","Panel Terms","Outside Counsel Guidelines","OCG","Framework Engagement Terms"])
_al("work_instrument","V5",["Engagement Letter","Letter of Engagement","Retainer Letter","Terms of Engagement","Matter Confirmation"])
_al("master","V6",["Terms of Business","ToB","Recruitment Agency Terms","Consultancy Agreement","Contractor Agreement","Employer of Record Agreement","Umbrella Company Terms"])
_al("master","V7",["Agreement for Lease","AfL","Lease","Underlease","Sublease","Licence to Occupy","Reversionary Lease","Wayleave"])
_al("change","V7",["Deed of Variation","Rent Review Memorandum","Licence to Alter","Licence to Assign","Break Notice"])
_al("master","V8",["Master Lease","Master Hire Agreement","Equipment Lease","Hire Purchase Agreement","FM Contract","Facilities Management Agreement"])
_al("master","V9",["Logistics Services Agreement","3PL Agreement","Warehousing Agreement","Carriage Agreement","Freight Agreement","Customs Brokerage Agreement","Fleet Lease"])
_al("shared_terms","V9",["RHA Conditions","BIFA Conditions","CMR Conditions"])
_al("master","V10",["Facility Agreement","RCF","Revolving Credit Facility","Invoice Finance Agreement","ISDA Master Agreement","Insurance Policy","Credit Insurance Policy"])
_al("security","V10",["Debenture","Charge","Intercreditor Agreement","Security Agreement"])
_al("component","",GEN_COMPONENT,"generic component cluster; family-neutral")
_al("change","",["Amendment","Variation","Deed of Variation","Side Letter","Extension Letter","Amended and Restated Agreement"],"generic change cluster; family-neutral")
_al("change","",["Addendum"],"ambiguous: amendment in one usage, new component in another; assign by what it does")
_al("order","",["PO","Purchase Order","Order","Call-off","Sales Order","Web Order"],"generic order cluster")
_al("order_response","",["Order Acknowledgement","Order Confirmation","Acknowledgement of Order","Quotation","Quote","Proforma"],"response side of the order flow")
_al("master","O3",["NDA","Non-Disclosure Agreement","CDA","Confidentiality Agreement","oneNDA","LOI","Letter of Intent","Heads of Terms","MOU","Memorandum of Understanding","Teaming Agreement"])
_al("security","O1",["Guarantee","Parent Company Guarantee","Bank Guarantee","Personal Guarantee","Promissory Note","Post-Dated Cheque","Letter of Credit","LC","Standby Letter of Credit","Performance Bond"])
_al("master","O2",["Settlement Agreement","Standstill Agreement","Tomlin Order","Consent Order"])
_al("component","O6",["DPA","Data Processing Agreement","Data Processing Addendum","SCCs","Standard Contractual Clauses","IDTA","Joint Controller Agreement"],"DPA here = data processing; collides with S9 deviated pricing")
_al("component","O5",["EDI Agreement","EDI Schedule","Trading Partner Agreement","cXML Agreement","PunchOut Schedule","API Schedule"])

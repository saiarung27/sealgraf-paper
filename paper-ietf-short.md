Network Working Group                                          S. A. Gunuganti
Internet-Draft                                                 Sealgraf
Intended status: Informational                                 November 2026
Expires: May 2027


     Owner-Approved Agent Spending with Sealed Evidence:
     The Approval-Evidence Object for Agent Action Protocols

                    draft-gunuganti-agent-approval-evidence-00


Abstract

   When a software agent acts for a person — in particular when it
   spends the person's money — the approval at the centre of the
   flow is, in current agent protocols, a statement by the agent
   itself. The Personal Agent Protocol's Operations extension
   states the consequence in its own security considerations: an
   approval there does not prove that the user saw the terms or
   approved them; it "works on trust". This document describes the
   design of a running system that removes the trust step for the
   approval half of the problem — an owner-set, machine-checkable
   mandate; a deterministic check performed and recorded before any
   spendable token exists; approval by the owner on a surface the
   agent cannot operate or imitate; a single-use decision token
   bound to the hash of the exact action approved; and a sealed,
   owner-held receipt that grades its contents (approval PROVEN;
   the performer's completion report, including payment facts,
   REPORTED and PINNED) — and specifies an optional
   approval-evidence object that agent action protocols can carry
   so that a relying party can verify an approval mechanically
   instead of trusting the agent's assertion.



Table of Contents

   1.  Introduction
   2.  Conventions and Terminology
   3.  The Approval Problem
   4.  The Approval-Evidence Object
   5.  Verification of the Object
   6.  A Running Implementation (Informative)
       6.1.  Design Overview
       6.2.  The Mandate and the Check
       6.3.  The Approval Surface and the Decision Token
       6.4.  Sealing and Verification Principles
       6.5.  Evidence Grades
       6.6.  Operating Record
   7.  Relationship to Other Work
   8.  Open Issues
   9.  Security Considerations
   10. Privacy Considerations
   11. IANA Considerations
   12. References
       12.1.  Normative References
       12.2.  Informative References
   Author's Address

1.  Introduction

   An automated agent that spends its principal's money creates a
   question that someone — a merchant, an issuer, an arbitrator,
   the principal — will eventually ask: what exactly did the owner
   approve, under what limits, and what happened next?

   Agent protocols currently answer the middle of that question
   with an assertion by the agent. In the Personal Agent Protocol
   (PAP) Operations extension, a Company proposes an action with
   exact, immutable terms; the user's Personal Agent obtains the
   user's approval; the Company performs the action at most once.
   The approval the Company receives is the agent's statement that
   the user approved. The extension's security considerations
   (Section 8.1 of Operations version 2, protocol draft 0.3) state
   the limit directly:

      "It doesn't prove that the User saw the terms or approved
      them. The Company can't see the Personal Agent's interface,
      so an approval works on trust, like the sign-in types. A
      Company MAY revoke the client_id of a Personal Agent that
      sends an approval the User didn't give. A Company that needs
      proof of the User's approval for an action can ask the User
      to approve on its own website, signed in, the way Direct
      Sign-In works. This extension doesn't define that step.
      Approvals the User signs are an open topic."

   Three properties of this arrangement generalize beyond PAP,
   which is simply the design that states them honestly:

   *  The attestor is the constrained party: the agent is the
      actor whose behaviour the approval is meant to constrain,
      and an approval channel the agent speaks through cannot
      distinguish a real approval from a fabricated one.

   *  The approval surface is the agent's interface, which neither
      the relying party nor a later arbitrator can see.

   *  The record belongs to someone other than the principal: the
      owner, whose money moved, holds no artifact of their own.

   This document describes a system, in production since
   2 November 2026, designed against those three properties, and
   derives from it a protocol object (Section 4) proposed for
   The design position taken in this document exists for a
   reason larger than the disputes the mechanism settles. As
   agents begin to spend, shop, and commit on a principal's
   behalf, the default outcome, unless it is designed against,
   is that the principal quietly ceases to be the owner of
   their money in any practical sense: the agent acts, the
   platform attests, and the principal's part is reduced to
   having once agreed to terms they never saw. The position
   taken here is the opposite. The owner sets the terms in
   advance, decides personally above a line they chose, and
   holds the evidence themself. Delegation does not have to
   mean surrender: an agent can be given real power to act
   while the authority over the money, and the proof of how it
   was used, stays with the person whose money it is.

   adoption by agent action protocols. The system is Sealgraf, an
   approval-and-evidence layer for agent spending: it checks, it
   records, and it never moves money.

2.  Conventions and Terminology

   The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL
   NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED",
   "MAY", and "OPTIONAL" in this document are to be interpreted as
   described in BCP 14 [RFC2119] [RFC8174] when, and only when,
   they appear in all capitals, as shown here. (In this -00 draft,
   the normative force attaches to the approval-evidence object in
   Section 4 and its verification in Section 5; the system
   description in Section 6 is informative and states what the
   reference implementation does.)

   Owner:        The person whose money an agent spends; the
                 principal. ("User" in PAP; "principal" in
                 [I-D.izmaylov].)

   Agent:        Software that proposes and performs purchases
                 for the owner.

   Mandate:      The owner's standing permission, expressed as
                 data: a sequence of immutable versions, each
                 carrying the agent it covers, a category
                 allowlist, a per-purchase cap, a rolling period
                 cap, a currency, a validity window, and an ask
                 line.

   Ask line:     The amount above which a purchase requires the
                 owner's personal decision, whatever the standing
                 permission otherwise allows.

   Action:       One proposed purchase: agent, category, amount in
                 integer minor units, currency, counterparty,
                 description.

   Action hash:  The SHA-256 digest of the canonical encoding of
                 an action; the identifier every downstream record
                 cites.

   Check:        The pre-spend evaluation of an action against the
                 current mandate version, performed by a
                 deterministic rule engine.

   Decision:     The check's sealed outcome: allow, deny, or
                 needs-owner-approval, with a stable reason code.

   Decision token:  A single-use, short-lived token minted only
                 after an allowing decision has been recorded,
                 bound to one action hash.

   Approval:     The owner's personal decision on an escalated
                 action, made on the owner's own authenticated
                 surface and sealed as its own statement.

   Completion:   The performer's post-spend report: completed
                 amount, merchant reference, and optionally a
                 payment block.

   Receipt:      The sealed, owner-held bundle joining the cited
                 mandate version, the action, the decision, the
                 approval statement when one was needed, and the
                 completion.

   Doorbell:     A notification (email, push) that carries facts
                 and a link to the approval surface, and never the
                 decision controls.

3.  The Approval Problem

   Standing permissions widen the problem of Section 1. Operations
   version 1 permitted a confirmation to cite a standing_permission
   — the user's earlier blanket permission in free text — with no
   machine-checkable form and no way for the Company to verify
   that the permission covered the terms. Version 2 withdrew the
   delegated form: the Personal Agent "MUST NOT approve one on the
   User's behalf, even when the User said earlier that they would
   approve something like it." That solves fabrication by removing
   delegation; but delegation is the normal case for a spending
   agent. An owner who must personally approve every purchase has
   a notification service, not an agent.

   The design position of this document is that per-action
   approval and standing permission are both necessary, and that
   both become evidence problems with the same shape: express the
   permission as machine-checkable data; move the per-action
   approval off the agent's surface; bind it to the exact terms;
   record it before anything spendable exists; and give the
   resulting artifact to the owner.

4.  The Approval-Evidence Object

   The concrete proposal to the community. PAP Operations (and, in
   shape, any agent action protocol) can define an OPTIONAL
   approval-evidence object, carried with or fetched after a
   confirmation, by which an approval service attests a user
   approval in a form the relying party can verify mechanically.
   The object states:

      operation_id, revision      the operation the approval covers
      operation hash              hash of the exact terms object,
                                  canonically encoded
      mandate id + version        the standing permission the
                                  approval was judged under
      approver                    the authenticated identity of the
                                  approver, and its authentication
                                  context (method and freshness, as
                                  recorded by the surface)
      outcome                     approval or refusal
      decision time               when the owner decided
      terms digest context        the mandate version's sealed
                                  digest, where limits exist
      service signature           over the canonical object, with
                                  the service's keys discoverable
                                  from the service's domain

   Three properties do the work, and a protocol carrying the
   object SHOULD require all three of an implementation that
   issues it:

   *  Third-party-verifiable. The object is signed by the approval
      service, and the keys are discovered from the service's
      domain — no prior bilateral relationship between the relying
      party and the service, and no shared secret with the agent.

   *  Independent of the agent. Issuance MUST NOT depend on any
      assertion by the agent whose spend is being approved — which
      is precisely the gap Section 8.1 of PAP Operations names.

   *  Bound to the exact terms. The object cites the operation's
      revision and a hash of the canonical terms object, so terms
      edited after approval fail verification rather than silently
      riding the approval.

   Three further properties, from operation, constrain how the
   object is produced:

   *  Record before token. The decision exists as a durable record
      before anything spendable or performable is issued from it.
      An attestation that can be minted before the decision is
      recorded attests to nothing.

   *  Refusals are first-class. If approvals carry evidence and
      refusals do not, an agent (or a service) can silently retry
      refused actions. The outcome field covers refusal, and a
      relying party that has seen a recorded refusal of the same
      terms can treat it as final.

   *  Approval is not performance. The object proves the approval.
      What happened next — the company's result, or in payments
      the settlement — is a separate report by the performer,
      graded separately (Section 6.5), and the two are never
      merged into one claim.

5.  Verification of the Object

   Verification for the relying party is mechanical:

   1.  Check the service signature over the canonical object,
       against keys discovered from the service's domain.
   2.  Check that the operation identifier and revision match the
       ones the relying party issued, and have not expired.
   3.  Check the terms digest against the terms the relying party
       proposed.
   4.  Only then perform, under the carrying protocol's existing
       at-most-once rules.

   With such an object, an approval stops being a claim the
   relying party trusts and becomes evidence it checks — the same
   posture the Operations extension already takes toward the
   performance result (the Company verifies the action executed
   exactly once, by operation id). Adoption asks nothing more of
   the protocol than a place to carry the object and a rule that,
   when one is present, it is verified rather than trusted.

6.  A Running Implementation (Informative)

   This section describes, at the level the companion paper
   [SEE-PAPER] uses, the production system from which Section 4's
   object is derived. It is an existence proof, not a format
   specification: the implementation's field-level format is
   documented separately and is not part of this document.

   6.1.  Design Overview

   Sealgraf interposes a check between an agent and its spending,
   without touching the spending itself:

   1.  The owner sets a mandate (Section 6.2).
   2.  Before spending, the agent submits the action for a check.
       Within limits, the decision allows and a decision token is
       minted. Above the ask line, the owner is notified via a
       doorbell and decides personally (Section 6.3). Outside
       limits, the decision denies, with a reason code.
   3.  The agent claims its token, spends on any rail (a wallet, a
       card, PayPal — Sealgraf is not in the payment path), and
       reports completion.
   4.  The receipt seals, graded as specified in Section 6.5. The
       owner holds it and can export a bundle that any party
       verifies offline.

   The agent reaches the check over MCP (a tool named
   check_permission) or over REST. Every act in the flow — mandate
   version, decision, approval, refusal, abort, completion — is
   appended to a per-owner hash chain and sealed (Section 6.4).

   6.2.  The Mandate and the Check

   A mandate is a sequence of immutable versions; every owner
   change creates a new version, and every decision cites the
   exact version it was judged under. One version's terms carry:
   the agent it covers; a category allowlist; a per-purchase cap;
   a rolling period cap; a currency; a validity window; the ask
   line; and a status (active, paused, revoked). Amounts are
   always integer minor units plus a currency code. Mandates are
   owner-set and never agent-editable; a revoked mandate cannot be
   revised.

   A version may also carry a step-up line: the amount at or above
   which an approval records, in its authentication context,
   whether a fresh-authentication requirement was in force and
   satisfied. When unset, the reference implementation derives the
   line from the ask line.

   The decision is a deterministic function of (mandate version,
   period spend so far, proposed action, time): no model is
   anywhere in the decision path, which is what makes a decision
   auditable and a receipt meaningful. Rules fire in a fixed
   order: agent identity; mandate status and validity window;
   scope (currency, positive amount, category allowlist,
   per-purchase cap); period cap; and the ask line, which
   escalates to the owner. Every outcome carries a stable reason
   code. The counterparty and description are exactly what the
   approver reads before allowing a spend, so the check boundary
   screens them for display spoofing (bidirectional-override and
   control characters), enforced in the engine — the choke point
   every transport passes through.

   The decision is persisted to the ledger BEFORE any decision
   token exists; if persistence fails, no token is issued.
   Authorizing reserves against the period cap — usage counts
   completed amounts plus outstanding unexpired reservations, and
   decisions are serialised per mandate — so two concurrent checks
   cannot both spend the same headroom, and an approval
   re-validates the reservation before anything is minted.

   Decisions that shape the ask channel itself (an exhausted ask
   budget, a cooling-off period after repeated refusals) are deny
   decisions sealed like any other: they mint no token and reserve
   nothing, but they are recorded. The owner's refusal is never
   shaped; only the agent's future asking is.

   6.3.  The Approval Surface and the Decision Token

   An escalated check notifies the owner (email, push) with the
   facts and a link — a doorbell, never the door. The Allow and
   Don't-allow controls exist only inside the owner's
   authenticated session on the approval service's surface. No
   approval can be given through any channel the agent can
   originate. This, and not the later signature, is what makes the
   approval hard to fabricate.

   An approval is sealed as its own statement, carrying: the
   action hash approved; the authenticated principal who approved
   — recorded as an authenticated principal and role, never a
   free-text label; the mandate version the approval was judged
   against, re-validated at approval time against the current
   version (status, window, scope, period headroom), not merely
   the version in force when the agent first asked; the approval
   time; and, for approvals at or above the step-up line, the
   authentication context (method and freshness, as recorded by
   the surface). Freshness is recorded, not judged: verifiers
   display it and apply no verdict to it; whether a recorded
   freshness is good enough is the reader's policy.

   Approval mints a decision token: single-use, bound to the
   action hash, valid for 15 minutes, stored only as a hash. The
   token is escrowed encrypted for exactly the credential that ran
   the check, which may claim it after the decision — claim is not
   consumption — so an agent that was offline when the owner
   decided can still collect the token, spend, and complete when
   it returns, with no new check and no broader access. In
   operation, agents arm a claim poller (polling roughly every 30
   seconds after firing an ask) so the owner's tap alone drives
   claim, payment, and completion.

   Refusals are first-class. If the owner refuses a purchase from
   the pending state, the refusal seals; an unchanged re-check of
   the same action is then denied by name
   (action_previously_denied), keyed by the action hash and
   deliberately surviving later mandate revisions: editing the
   limits does not resurrect a refused purchase.

   Approval is not the last check. At completion, the engine
   re-validates the token, its expiry, and the mandate's current
   status and scope: a pause, revoke, or tightening revision that
   lands between approval and spending stops the spend.

   6.4.  Sealing and Verification Principles

   Every act in the flow is appended to a per-owner hash chain:
   each entry's hash covers the previous entry's hash and the
   exact payload bytes; payloads are stored as the bytes that were
   signed; and every append first verifies the current chain head,
   so a corrupted head is refused rather than sealed over. Entries
   are in-toto-shaped statements [INTOTO] carried in DSSE
   envelopes [DSSE], each envelope dual-signed (Ed25519 and ECDSA
   P-256; the P-256 key is held in a cloud KMS and is
   non-exportable), and signing covers the pre-auth encoding of
   the exact payload bytes — verification never re-serializes a
   payload to check it.

   Periodically, the chain is checkpointed: a Merkle tree head
   over the entries is dual-signed, and the checkpoint digest —
   the only bytes that leave the operator — can be witnessed
   externally (in the current deployment, by two independent
   RFC 3161 timestamp authorities [RFC3161]; OpenTimestamps
   witnessing is supported by the same machinery). Checkpoints are
   currently volume-triggered, which Section 8 names as an open
   issue.

   The receipt is the owner's artifact: one sealed bundle holding
   the cited mandate version's terms, the action and its hash, the
   decision, the approval statement when one was needed, and the
   completion block. Bundles export into an offline package — exact
   signed bytes, public keys, chain position, and a Merkle
   inclusion proof into a dual-signed checkpoint — that a verifier
   checks with no account, no API key, and no trust in the
   operator's servers.

   An approval inside a bundle is PROVEN only when its entry is
   included in a checkpoint that itself verified (anchored);
   chain linkage alone is arithmetic a presenter could recompute
   over a fabricated statement, so an unanchored approval is
   reported as exactly that — unanchored, unproven — and a bundle
   whose receipt required approval but carries no approval
   statement fails verification outright. Approval can never be
   silently absent from the package that claims it happened. A
   claim stronger than its proof (for example, an anchor state of
   "pending" presented as "anchored") is a verification failure,
   not a warning.

   The verifier keeps two verdicts separate, and the separation is
   part of the format: authenticity (the bytes are what the signer
   sealed and have not mutated) and currency (whether the cited
   mandate is still in force now — which offline verification
   cannot check and reports as not checked).

   The online checker applies the same custody discipline in the
   other direction: a receipt number alone opens nothing for a
   non-owner (it is a label anyone may photograph, not a
   credential); the receipt's check code — known to the owner and
   whoever they show it to — is the key. Receipt numbers are
   assigned sequentially within an owner's chain.

   6.5.  Evidence Grades

   The record's central discipline is that its contents carry
   different evidence grades, and the grades travel with the
   artifacts to every reader, including verifiers:

   *  APPROVAL — PROVEN. The owner approved these exact terms, on
      a surface the agent could not operate. Proven when the
      approval statement is anchored (Section 6.4); an unanchored
      approval is honestly reported as unproven, never upgraded.

   *  TERMS — PROVEN when anchored, by the same rule.

   *  DECISION — PROVEN as the service's sealed record of its own
      act. Decisions are deterministic given their inputs; the
      period-cap leg depends on live usage and is not re-judged
      offline.

   *  COMPLETION — REPORTED AND PINNED. The performer reports what
      it did — merchant reference and payment block — and the
      report is sealed byte-identically into the receipt; a later
      edit is detectable, and the report is attributable. Sealing
      does not convert a report into a witnessed fact. A
      completion is sealed even when it reports a charge above the
      authorized amount: refusing it would erase the only durable
      record of the overcharge; the comparison belongs at read
      time.

   *  COUNTERPARTY-SIGNED SETTLEMENT — NOT HELD. No merchant,
      issuer, or rail signs the reference implementation's
      completion; where other frameworks obtain counterparty
      signatures (Section 7.2), their payment leg is stronger, and
      this design says so.

   6.6.  Operating Record

   The system has been in production since 2 November 2026, and
   the full loop — agent check, owner approval, automatic token
   claim, purchase on a real rail, sealed receipt — has run
   end-to-end with real money. On 2 November 2026, an agent
   checked a USD 10.27 purchase (PayPal rail) that proceeded under
   the standing mandate and sealed receipt No. 000019; a second
   purchase the same day (USD 9.72, paid with a Stripe Link
   one-time virtual Visa) sealed receipt No. 000025, which carries
   the payment block. The same day, in one production instance, an
   identical re-check of a purchase the owner had declined was
   denied by name (action_previously_denied) — a refusal bound a
   later presentation of the same action, not only in tests. On
   3 November 2026, a USD 9.98 purchase sat above the owner's ask
   line, so the check escalated; the owner approved from their
   phone; the agent's claim poller collected the decision token
   automatically; the purchase completed through Stripe Link
   (charged USD 9.72, as reported) and sealed as receipt
   No. 000030, publicly checkable by anyone the owner shows its
   check code to (the code is printed in the companion paper
   [SEE-PAPER]).

   Production state as of 7 November 2026: 257 accounts, 216
   tenants, 1,868 ledger entries, 103 sealed receipts, 26 agent
   connections. The caveat belongs in the text: almost all of
   those accounts are the operator's own test accounts, and the
   number of external users is zero. The operating evidence
   therefore supports claims about the mechanism — that the loop
   runs, that approvals bind, that refusals hold, that receipts
   verify — and no claims about adoption, usability at scale, or
   owner behaviour in the wild.

7.  Relationship to Other Work

   The individual pieces of this design are all claimed somewhere,
   and this document claims none of them. What it offers is a
   deployed combination — a permission artifact, an enforced
   check, an approval surface independent of the agent, an
   owner-facing payment record, and owner-held sealed evidence, in
   one running loop — and the distinctions that combination makes
   visible:

   7.1.  PAP Operations. Closest in spirit. Its exact, immutable
   terms and proposed standing permissions are the direct
   ancestors of the mandate (Section 6.2); Sections 3 and 4 are
   this document's answer to its Section 8: per-action approval on
   the owner's own surface, standing permission in
   machine-checkable form, and the approval-evidence object
   offered back to the protocol. No conformance is claimed: the
   reference implementation exposes the check through its own MCP
   tool and API, not through a PAP implementation.

   7.2.  Agent Payments Protocol (AP2, v0.2, April 2026; FIDO
   Alliance). Mandates are user-signed on a non-LLM Trusted
   Surface, and AP2's payment leg is stronger than this design's
   where it applies — Checkout and Payment Receipts are SIGNED BY
   THE MERCHANT AND THE PAYMENT PROCESSOR and hash-bound to the
   mandate, the counterparty-signed proof Section 6.5 marks as not
   held. AP2 answers payment-proof inside AP2 flows; the approval
   object here answers approval-proof for any agent on any rail,
   before the spend rather than at settlement.

   7.3.  Mastercard Verifiable Intent (v0.1 draft, March 2026;
   pilots from February 2026). Couples intent cryptographic
   objects to agentic tokens on network infrastructure, with the
   issuer's step-up inside the card network — stronger
   institutional binding inside that network, and, by the draft's
   own terms, consulted rather than held (pre-transaction). It is
   Mastercard-rails-only; this design is rail-agnostic and
   owner-custodied.

   7.4.  Agent receipts (Asqav; [I-D.marques-asqav]). Signed
   receipts of agent actions with post-quantum signatures (ML-DSA),
   including a bilateral pairing of approval and outcome receipts
   — the closest receipt-layer neighbours. The differences are of
   subject: Asqav signs ACTIONS for organizations (its terms
   exclude consumers' personal use) and its approval records "do
   not pause/resume agent execution" — evidence about flows a
   control plane governs elsewhere. This design's artifacts are an
   OWNER's approval and the payment facts around a purchase, and
   its check executes.

   7.5.  Signed permission-and-receipt drafts [I-D.izmaylov]. The
   closest standards-layer neighbour, and the most instructive
   comparison. The draft's principal signs the permission with a
   passkey — a stronger identity act than the account session
   behind the approvals described here — with mechanically
   checkable limits (amounts, methods, categories, counterparty,
   cadence), and its records are, in its own framing, "evidence,
   not enforcement", with an executor role named but its decision
   procedure expressly unspecified. The designs differ on both
   axes at once: the signature is the draft's evidence; here the
   evidence is the approval's provenance — an accountable
   principal's recorded act, on a surface outside the agent's
   reach — plus an enforcement point the draft deliberately
   leaves open. The verifier's questions differ accordingly: the
   draft reports soundness, signature validity, and
   within-permission as separate answers; the verification here
   adds the anchor discipline of Section 6.4.

   7.6.  x402. A payment protocol whose signed authorization IS
   the settlement, on-chain: the strongest possible payment proof,
   for stablecoin payments. It represents no owner permission and
   issues no owner-facing approval record; the problems are
   adjacent, not the same.

8.  Open Issues

   *  Interception honesty. An agent that never calls the check
      leaves no receipt, and the reference implementation cannot
      stop it — the agent is software the owner chose to run.
      Adoption makes evasion visible rather than impossible: the
      owner can reconcile "purchases with receipts" against card
      statements, and a checked agent that goes silent is itself a
      signal. The realistic mitigations are platform-shaped: wallet
      and issuer defaults that ask for a decision token,
      operating-system agent frameworks with the check built in.
      The design supports those integrations; it does not pretend
      to be them.

   *  Checkpoint cadence. Section 6.4's volume trigger leaves
      low-volume owners' approvals unanchored for long stretches —
      PROVEN only at anchor. The direction under consideration is
      a signed tree head per sealing event plus a published anchor
      clock; not yet implemented, and this draft's claims do not
      include it.

   *  Test asks. The implementation has no test flag. Test checks
      run as ordinary asks, distinguished only by unique test
      items, so denial memory never meets production history; an
      unflagged test counts against the period total while pending,
      and a refused test is a real refusal in denial memory.

   *  Platform trusted surfaces. AP2's Trusted Surface and the
      card networks' issuer flows are stronger approval UX than a
      web surface; this design's surface-independence argument
      cuts both ways — the owner approves somewhere the AGENT
      cannot reach, but also somewhere the PLATFORM does not
      mediate. An approval service whose surface renders inside a
      platform's trusted UI, without surrendering record custody,
      is the open design problem.

   *  Owner-signed mandates. A neighbouring design (Section 7.5)
      has the owner sign the permission with their own key — a
      stronger identity act than the authenticated session behind
      the approvals described here. The counterweight is ceremony:
      key loss, device change, and recovery become owner-facing
      problems for a non-technical owner population. The trade is
      unresolved, and this design has not taken it.

   *  Scope. The system judges purchases (category, amount,
      counterparty, window). Other agent actions — messages sent,
      files changed, bookings made — share the approval-evidence
      shape; nothing here claims they are solved.

9.  Security Considerations

   Signing-oracle surface. A sealing service that signs
   caller-supplied bytes is an oracle; the reference implementation
   signs only fixed-schema payloads constructed by the sealing
   path, and its production P-256 key is non-exportable in a cloud
   KMS.

   Record before token. Any implementation of this design MUST
   persist the decision before minting anything spendable
   (Section 6.2): a crash between decision and record would
   otherwise create spendable authority with no evidence.

   Token custody. Decision tokens are single-use, short-lived,
   hash-stored, and bound to one action hash; the escrow/claim
   discipline of Section 6.3 ensures an unclaimed token's plaintext
   dies with its preauthorization's terminal transition.

   Presenter fabrication. The most dangerous forgery is not
   against the signed receipt but against the UNSIGNED records
   around it: a presenter who fabricates an approval statement and
   recomputes the chain arithmetic over it. Section 6.4's anchor
   discipline — PROVEN only when a dual-signed checkpoint covers
   the entry and the inclusion proof recomputes — is the
   countermeasure, and verifiers MUST NOT soften it. The
   symmetrical rule closes the hole for receipts: a correctly
   hashed but unsigned entry is a forgery, however well it links.

   Anchor overclaim. A state presented stronger than its proof is
   a verification failure (Section 6.4), in implementations as in
   bundles: "pending" MUST NOT render as "anchored".

   Denial memory abuse. Because an owner refusal permanently
   denies the identical action, an attacker who can induce
   refusals can block legitimate purchases; ask shaping
   (Section 6.2) bounds the ask channel, and owners can always
   re-scope a purchase (different amount, category, or
   counterparty) to escape a stale refusal.

   PAN screening. Completions are scanned for full card numbers
   and refused if found; the payment block has no field a full
   card number could legitimately occupy.

   Display spoofing. Counterparty and description strings are
   attacker-influenced and are what the approver reads;
   bidirectional and control characters are screened at the engine
   boundary (Section 6.2), and renderers of sealed artifacts MUST
   escape rather than interpret carried text.

   Key compromise. Key-registry status transitions (active /
   verify-only / compromised) bound the blast radius: a
   compromised key's signatures MUST NOT be relied upon, and the
   dual-signature policy means one algorithm's compromise alone
   does not authenticate an envelope.

10.  Privacy Considerations

   De-identified approvers. Approval statements name the approver
   by authenticated principal and role only: never a personal name
   or email address, so a receipt shown to a merchant or
   arbitrator does not carry the owner's identity beyond the role
   that acted.

   Hash-only anchoring. Anchors disclose exactly one SHA-256
   digest per checkpoint to third-party witnesses (Section 6.4);
   no terms, amounts, or identities leave the operator for
   anchoring.

   Receipt numbers are not credentials. A receipt number is a
   chain position, and checkers MUST treat possession of the check
   code — not the number — as the capability (Section 6.4).
   Implementations of number-based lookup MUST NOT leak existence
   across owners (uniform not-found responses).

   Purchase data sensitivity. A receipt records categories,
   amounts, counterparties, and instrument last-fours — financial
   facts about the owner. Custody is the mitigation: the artifact
   is the owner's, held for the owner, exportable by the owner,
   and shared at the owner's direction.

11.  IANA Considerations

   This document has no IANA actions.

12.  References

   12.1.  Normative References

      [RFC2119]   Bradner, S., "Key words for use in RFCs to
                  Indicate Requirement Levels", BCP 14, RFC 2119,
                  DOI 10.17487/RFC2119, March 1997.

      [RFC8174]   Leiba, B., "Ambiguity of Uppercase vs Lowercase
                  in RFC 2119 Key Words", BCP 14, RFC 8174,
                  DOI 10.17487/RFC8174, May 2017.

   12.2.  Informative References

      [RFC3161]   Adams, C., Cain, P., Pinkas, D., and
                  R. Zuccherato, "Internet X.509 Public Key
                  Infrastructure Time-Stamp Protocol (TSP)",
                  RFC 3161, DOI 10.17487/RFC3161, August 2001.

      [DSSE]      "Dead Simple Signing Envelope (DSSE) protocol
                  v1.0" — Pre-Auth-Encoding as used in Section 6.4.

      [INTOTO]    "in-toto Attestation Framework — Statement and
                  Predicate model": statements of the form used in
                  Section 6.4.

      [PAP-OPS]   Salazar, E., "Personal Agent Protocol —
                  Operations extension (Purchase and Subscription
                  Operations)", protocol draft 0.3, Operations
                  version 1 (standing permission attestations) /
                  version 2 (Section 8.1 quoted in Sections 1 and
                  3), https://personalagentprotocol.org/docs/0.3/
                  extensions/operations .

      [PAP-ISSUE61]  "Agent-side shopping mandates (industry
                  alignment thread)", Personal Agent Protocol issue
                  #61, 2026-10-24 (author summary and thread as read
                  November 2026).

      [I-D.izmaylov]  Izmaylov, P., "Signed Permissions and Action
                  Receipts for Automated Agents",
                  draft-izmaylov-agent-permission-receipts-02,
                  31 October 2026.

      [I-D.marques-asqav]  Marques, J. A. Gomes, "Compliance
                  Profile of Signed Action Receipts for AI Agents",
                  draft-marques-asqav-compliance-receipts-09,
                  21 September 2026, and Asqav product documentation,
                  as reviewed November 2026.

      [AP2]       "Agent Payments Protocol (AP2), version 0.2",
                  April 2026; FIDO Alliance adoption; Trusted
                  Surface; merchant-signed Checkout Receipt and
                  processor-signed Payment Receipt.

      [MC-VI]     Mastercard, "Verifiable Intent, version 0.1
                  draft", March 2026 (pilots from February 2026);
                  pilot communications, 2026.

      [X402]      "x402 protocol" — HTTP 402 payment protocol;
                  signed authorization as settlement (stablecoin
                  rails).

      [SEE-PAPER]  Gunuganti, S. A., "Approval You Can Verify:
                  Owner-Approved Agent Spending with Sealed
                  Evidence", November 2026 (companion paper;
                  canonical text lodged with the author).

Author's Address

   Sai Arun Gunuganti
   Sealgraf
   Email: support@sealgraf.com
   URI: https://sealgraf.com

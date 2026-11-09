# Approval You Can Verify: Owner-Approved Agent Spending with Sealed Evidence

**Sai Arun Gunuganti** — Sealgraf (operated by Sai Arun Labs) — Contact: support@sealgraf.com

Technical paper, November 2026. License: Creative Commons Attribution 4.0 International (CC BY 4.0) — see `LICENSE`.

## Abstract

When a software agent spends a person's money, someone must be able to answer, later and to a third party: what exactly did the owner approve, under what limits, and what happened next? Current agent protocols answer the first part of that question with a statement by the agent itself. The Personal Agent Protocol's Operations extension states the consequence in its own security section: an approval there "doesn't prove that the User saw the terms or approved them" — it "works on trust." This paper describes a system, running in production, that removes the trust step for the approval half of the problem. An owner sets machine-checkable limits in advance (a *mandate*). A deterministic engine decides, and the decision is persisted and sealed before any spendable token exists. Purchases above an owner-set line are decided by the owner personally, on the owner's own authenticated surface — a surface the agent can notify but cannot operate, imitate, or replay. The result is a sealed, one-owner receipt in which two grades of fact are kept deliberately separate: the approval is *proven*; the performer's report of what happened next, including the payment details, is *reported and pinned*. The paper states the design, the evidence model, the operating record so far (including its limits), the relation to neighbouring work — the Personal Agent Protocol, AP2, Mastercard Verifiable Intent, Asqav, the Izmaylov permission-receipts draft, and x402 — the open problems, and a concrete proposal: an approval-evidence object that protocols like the Personal Agent Protocol's Operations extension could carry, so that a company which needs no more than trust can verify an approval mechanically.

## Contents

- `paper.md` — the canonical paper (Markdown source of truth).
- `sealgraf-paper.pdf` — the paper rendered as a PDF (title page + body; rendered from `paper.md` on 9 November 2026).
- `paper-ietf-short.md` — the Internet-Draft preparation text (`draft-gunuganti-agent-approval-evidence`); RFCXML conversion, idnits, and Datatracker submission are separate steps.
- `LICENSE` — CC BY 4.0.

## Status

Prepared for publication on 9 November 2026. Venue submissions (Zenodo, SSRN, ResearchGate, arXiv, IETF Datatracker) and the canonical page at sealgraf.com are tracked in the publication record; DOIs and venue URLs will be added here as they are issued.

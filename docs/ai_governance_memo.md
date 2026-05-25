# Memo: Responsible AI/ML governance at MTA

**To:** Hypothetical reader. This memo is a portfolio piece, not an
official MTA document.
**From:** Siddhant Rajhans
**Date:** May 2026

## What this memo covers

MTA has signaled in 2025-2026 that it intends to use AI more aggressively:
camera analytics for safety, fare-evasion detection, predictive
maintenance, AI-assisted procurement. Some of this is already in pilot
form. Civil rights groups have pushed back on the surveillance pieces.
The question I'm trying to answer here is what a minimal-but-real
governance framework would look like, given the actual constraints.

It's a one-pager. A real framework would be longer. This is the version
I'd hand a manager who has 10 minutes before a board meeting.

## The regulatory landscape, briefly

Federal: there is no comprehensive federal AI law. The 2023 executive
order set direction; agency guidance has followed (NIST AI RMF 1.0 is
the practical reference). Treat NIST as the baseline.

New York State: AI accountability legislation has been proposed
repeatedly. Some of it will pass. The contours that consistently appear
are impact assessments, bias audits, and transparency for
high-consequence systems.

New York City: Local Law 144 applies to automated employment decision
tools. MTA hiring would fall under it. The deeper relevance is that the
city has shown it will write laws specific to AI use cases.

EU AI Act: not US law, but vendors selling to MTA may also sell into
Europe and will already be classifying their systems by risk tier
(unacceptable, high, limited, minimal). Knowing the tier of a vendor's
system makes procurement conversations faster.

## What I'd recommend, in priority order

**1. Inventory before policy.** Before writing rules, find out what AI
systems are already in use, planned, or in pilot. Across an agency the
size of MTA there are almost certainly more than anyone has counted. The
inventory should record: what the system does, who owns it, what data
it uses, what decisions it influences, and whether a human is in the
loop.

This is the single highest-leverage step. You cannot govern what you
have not catalogued.

**2. Tier the inventory by risk.** Borrow the EU AI Act's four tiers as
a rough sort. A camera that flags unattended bags on a platform is a
different governance problem than an internal procurement-drafting
assistant. Most of MTA's AI work probably falls into the "limited" or
"high" tiers; very little should be in "unacceptable."

**3. Require impact assessments for high-tier systems.** Before any
high-tier AI system goes live, the owning team writes a short impact
assessment: what could go wrong, who could be harmed, what tests show
the system performs acceptably for affected groups, what the rollback
plan is. Five pages, not fifty.

**4. Designate model and data stewards.** Every deployed model has one
named person responsible for it. Every dataset feeding a model has one
named person responsible for its quality. These can be the same person
or different. Without named owners, governance is theater.

**5. Build a public-facing AI use page.** Eventually, riders will ask
which AI systems they're encountering when they ride the subway. A
public-facing page describing each system in plain English, what it
does, and what data it uses, would get ahead of the trust problem.

## What this would cost, roughly

Inventory: one analyst for two months. Risk tiering: same analyst, two
weeks. Impact assessment template: one week to write, then ongoing
overhead of maybe a week per new high-tier system. Stewardship
designation: organizational, not technical, but real time from senior
managers. Public-facing page: small. The expensive part isn't building
the framework; it's keeping it current as MTA's AI footprint grows.

## What I'm not addressing

The hard policy questions about whether MTA should deploy AI camera
analytics at all. That's a values question that goes above this memo.
This memo assumes deployment is happening and asks how to do it
responsibly.

## References

- NIST AI Risk Management Framework 1.0, January 2023.
- NYC Local Law 144 of 2021, on automated employment decision tools.
- EU AI Act, Regulation (EU) 2024/1689.
- Executive Order 14110 on Safe, Secure, and Trustworthy AI, October 2023.
- MTA RFI for AI video analytics, late 2025.

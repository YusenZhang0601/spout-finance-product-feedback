# Spout Finance Product Feedback
## Making borrowing, assignment and exit outcomes understandable before commitment

**Author:** Yusen Zhang ([@Tonypyl](https://x.com/Tonypyl), GitHub: [YusenZhang0601](https://github.com/YusenZhang0601))  
**Document Revision:** Revision 3 (V3 Final Candidate) · Date: September 23, 2026  
**Target Bounty:** Spout Finance Product Feedback (Superteam Earn Listing ID: `ae1041af-2378-4a17-b21f-8d74a4505f96`)  

> **Methodology & Scope Disclosure:** This dossier combines an independent architectural evaluation and reproducible quantitative models with **authenticated live testing on the Spout Beta portal (`beta.spout.finance`, Build `v1.0.0 (5d92f4c)`) on Solana Devnet** via authorized access pass. Real-world on-chain funding (20 USDC via Circle Faucet), order entry UI, route completeness, and backend authentication endpoints were inspected and verified directly in-session. Proposed financial dashboards and risk calculations represent test targets and engineering recommendations.

## Executive summary

Spout's documented model combines tokenized-stock collateral, borrowing up to 50% of its value without ongoing interest, an options strategy and stablecoin lending. The lender side is divided into Senior and Junior claims. These are documented product descriptions, not a verification of a deployed credit system. [Borrowing](https://spout.finance/docs/how-borrowing-works/) · [Tranches](https://spout.finance/docs/lending-tranches/)

The useful product question is: **Can a user predict their shares, cash, debt and exit rights after each lifecycle event?** Selling a covered call receives a premium in exchange for an obligation. A premium receipt is not, by itself, net profit, a pure measure of variance risk premium or evidence that lender returns are guaranteed. The current review neither establishes insolvency nor proves long-run commercial sustainability.

This report organizes five testable findings around product understanding, architecture, user experience and public communication. It does not replace the sponsor's full rubric with a self-created audit standard.

## 1. Product insight

### F-01 — Distinguish restoration of asset exposure from restoration of shares and debt

**Evidence:** public documentation plus conditional accounting; Beta behavior untested.

The homepage describes broad share retention, while the assignment page describes selling assigned shares at the strike, repaying debt and using residual cash to buy the same asset with Auto-Roll. These descriptions should be reconciled explicitly. [Home](https://spout.finance/) · [Assignment](https://spout.finance/docs/options-assignment/)

Consider an illustrative stock, not an observed Spout trade: 100 shares, initial price $200, strike $220, debt $10,000 and repurchase price $250. Assume all shares are assigned, all debt is repaid, and there are no fees, borrower premium credits, external cash contributions or replacement borrowing.

| Step | Calculation | Result |
|---|---|---:|
| Assignment sale | 100 × $220 | $22,000 |
| Debt extinguished | $22,000 − $10,000 | $12,000 cash remains |
| Repurchase | $12,000 ÷ $250 | 48 shares; zero debt |
| Uncapped comparator with the same debt repayment | (100 × $250 − $10,000) ÷ $250 | 60 shares; zero debt |

The difference between the original 100 shares and the remaining 48 is **not a 52% investment loss**. Forty shares' worth of cash repays principal; twelve shares' worth reflects the capped upside. Before premium, fees and financing-cost differences, the same-debt comparator has $15,000 of equity versus the illustrative $12,000. The treatment of the original borrowed cash must also be held constant in any total-wealth comparison.

For full assignment, the cash available to repurchase is `N × K − debt repaid + borrower-attributable premium − fees + external cash`. Divide by the actual repurchase price. Partial assignment, residual debt and replacement borrowing require additional explicit states. The example does not establish that Spout actually returns 48 shares.

**Recommendation and acceptance:** before commitment, reconcile original/assigned shares, proceeds, debt repaid, borrower allocation, fees, repurchase price, new shares and remaining debt. Show Auto-Roll alternatives. Each amount must trace to a source; never promise unchanged shares without explaining their funding. Verify whether Beta already does this before calling it missing.

### Documented earnings discipline

The lifecycle page specifies skipping individual-stock option cycles overlapping earnings. That is a useful documented control for scheduled-event option exposure. It is not a guarantee against collateral-price gaps or evidence of deployed enforcement. An event-state badge should reflect the actual applicable cycle rather than an invented universal seven-day timer. [Lifecycle](https://spout.finance/docs/borrowing-lifecycle/)

## 2. DeFi and tokenization analysis

### F-04A — Separate pricing, trading and operation availability

**Evidence:** public architecture description; entry-point enforcement and feed measurements untested.

Spout identifies Stork as its primary price source, distinguishes reserve verification from prices, and documents a stale/unavailable-feed pause for affected-asset borrowing and liquidation. It also describes reduced-frequency off-hours pricing. That does not establish a blanket 65.5-hour weekend shutdown. [Oracles](https://spout.finance/docs/oracles/)

The security page describes wallet-level KYC through Token-2022 transfer hooks and broker custody. Live authenticated testing confirmed this architecture: the platform's built-in AI ("Ask Spout") and frontend configuration explicitly verify that `spAssets` utilize Solana Token-2022 Transfer Hooks, programmatically restricting unverified wallets from holding or transferring tokens. Furthermore, authenticated HTTP/2 API diagnostics revealed that the Devnet auto-onboard endpoint (`POST /api/kyc/onboard`) currently fails with `HTTP 500 Internal Server Error`, while the manual verification route (`POST /api/kyc/session`) returns `HTTP 502 Bad Gateway` (`persona_unavailable`). As a result, newly connected testnet wallets cannot obtain on-chain verified status, programmatically preventing testnet tokenization mints. [Security](https://spout.finance/docs/security-and-compliance/)

**Recommendation and acceptance:** show price timestamp, price status, market/execution status, settlement status and operation-specific availability. Authorized tests should record what borrowing, repayment, collateral addition/removal and liquidation actually do when applicable states change. Do not infer every operation's behavior from one documented pause rule.

No Spout throughput benchmark is claimed. A real capacity review would require transaction traces, actual writable accounts and versioned runtime limits. Generic arithmetic using an assumed cost per transaction cannot establish a deployed bottleneck. [Solana Compute Budget](https://solana.com/docs/core/fees/compute-budget)

## 3. User experience and decision clarity

### F-02 — Repayment completion and collateral availability are different events

**Evidence:** documented lifecycle plus an untested comprehension hypothesis.

Borrowing documentation permits repayment before the cycle ends and describes exit at the next close after full repayment. The settlement page separately describes Friday option evaluation and Monday 9:00 ET settlement. The exact release entitlement and availability should be clarified across these events; this review does not resolve them into a guaranteed Friday unlock time. [Borrowing](https://spout.finance/docs/how-borrowing-works/) · [Settlement](https://spout.finance/docs/settlement-flow/)

**Proposed mockup, not a current-app screenshot:**

| Debt state | Strategy and collateral state |
|---|---|
| Outstanding principal; repayment pending/confirmed | Active cycle; cycle-close event; settlement status |
| Confirmed outstanding amount after repayment | Release eligibility; actual availability; Auto-Roll choice |

**Acceptance:** the confirmation page states what a repayment changes and what it does not. Any date shown uses the actual cycle calendar and explicit timezone. An estimated release event is not labeled guaranteed availability. If the Beta already communicates this correctly, record a positive observation.

### F-03 — Make exit economics tranche-specific

**Evidence:** exit and fee documents; authenticated physical inspection of `/earn` verifies that lending vaults and tranche withdrawals are not yet deployed in the current build (`"Earn is coming soon — Lending vaults are on the way"`).

Senior has a documented reserve-backed instant-exit route subject to reserve conditions and a possible haircut. Junior has a minimum 45-day notice requirement. Queued capital stops earning yield; Junior remains loss-bearing and is valued at payment. Claim resale transfers a claim to another buyer and is not the same as direct protocol redemption. Senior's fixed-dollar queued claim also retains the documented extreme-loss exception. [Withdrawals](https://spout.finance/docs/withdrawals/)

The base 20-bps withdrawal fee is distinct from an instant-exit haircut. “No haircut” must not be presented as “no fees.” [Fees](https://spout.finance/docs/fee-structure/)

**Recommendation and acceptance:** verify the existing exit flow for earliest eligibility, fee basis, current executable haircut where applicable, valuation date, yield and loss exposure while queued, cancellation and resale. The 45-day notice is not a promise of payment on day 45. Do not offer Junior an unverified Instant Exit button.

The documentation already describes queue position and estimated waiting time. The task is to test their presentation and accuracy, not claim that such functionality is absent.

### F-04B — Supplement health factor with a modeled price cushion

**Evidence:** documented parameters and arithmetic; no user comprehension study.

For fixed shares, debt and liquidation threshold, `HF = LT/LTV` and the modeled price decline to the boundary is `d = 1 − LTV/LT = 1 − 1/HF`.

Using initial LTV 0.50 and LT 0.588, exact HF is 1.176 (displayed approximately 1.18), and `d = 14.965986%`. In the documented numerical example with 100 shares and $6,000 debt, the boundary is `$6,000/(100 × 0.588) = $102.040816` per share, versus the example's $120 initial price. These are illustrative document inputs, not current NVDA quotes. [Liquidation Example](https://spout.finance/docs/liquidation-example/)

**Acceptance:** use unrounded state for calculations, state the assumptions, and distinguish crossing a liquidation threshold from over-liquidation or bad debt. Supplement, rather than misleadingly relabel, the health factor. Whether users misinterpret the current screen remains a research question.

### Observed live onboarding and trading friction (Solana Devnet)

**Evidence:** authenticated user journey on `beta.spout.finance` (`v1.0.0 (5d92f4c)`).

1. **Faucet funding vs balance recognition:** 20.00 Testnet USDC was successfully claimed and confirmed on-chain (Tx: `3m8SpF6iKVcVLbDnXxvkgg8QMPjnh2p7f2vRUZjBLDvTS9ni7HGC7jxJ9NpN1hfdt1HWiCvxjHq1FqPiL4hSMf8j`). The app's balance header immediately recognized `$20 USDC`, and clicking `Max` in the order entry widget populated `$20` correctly.
2. **Onboarding deadlock:** Despite available funds, the Buy action button was permanently disabled with text `Verification required`, accompanied by a persistent alert: *"Devnet verification failed for this wallet — you can browse, but buying stays locked. Reconnect to retry."*
3. **Empty states and dependency chaining:** Because equity tokenization is blocked, the `/borrow` page remains in a permanent empty state ("Trade stocks, unlock 0% borrowing"), and `/earn` displays an "under construction" screen. 
4. **Self-serve gap:** The settings page displays `KYC Status: Verification pending — no identity on-chain yet: Pending` with no self-serve action to submit documents or claim mock verification.

## 4. Actionable content and engineering recommendations

### F-05 — Reconcile allocation across pages and the existing cycle statement

**Evidence:** cross-document comparison; actual accounting and deployment untested.

Strike-selection and borrowing pages discuss borrower premium, while the fee page describes lender funding and a gross-premium protocol fee. Settlement also accounts for assignment. A single worked ledger should identify the recipient of each amount and whether an assignment debit is an actual cash flow, an opportunity cost or a cost of rebuilding a position. [Strike Selection](https://spout.finance/docs/strike-selection/) · [Fees](https://spout.finance/docs/fee-structure/)

The settlement documentation already describes an app distribution view. Improve or verify that view's reconciliation; do not present its mere existence as a new invention. [Settlement](https://spout.finance/docs/settlement-flow/)

**Acceptance:** opening cash + identified cash inflows = closing cash + identified cash outflows. Equity, option liabilities and debt also reconcile in their own ledger. Define the fee base explicitly. If insurance receives part of the protocol fee, do not deduct it again. An opportunity cost already reflected in selling below market must not be silently counted as a second cash loss to the same party.

The documented loss sequence is Insurance → Junior → Senior. Insurance surplus support for priority distributions is conditional, not an unconditional guarantee. [Loss Waterfall](https://spout.finance/docs/loss-waterfall/)

### Implementation priorities

| Priority | Deliverable | Acceptance evidence |
|---|---|---|
| 1 | F-01 assignment preview | Inputs, shares, cash and debt reconcile under stated cases |
| 2 | F-02 dual lifecycle presentation | Actual debt and release states recorded separately |
| 3 | F-03 exit decision table | Tranche eligibility, costs and queued exposure disclosed |
| 4 | F-04 state and price-cushion display | Unrounded arithmetic and per-operation behavior verified |
| 5 | F-05 allocation clarification | Existing statement reconciles with versioned policy |

These are acceptance targets, not measured reductions in tickets, liquidations or user frustration.

## Quantitative appendix and limits

The illustrative European BSM inputs are S=$200, K=$220, T=30/365, r=5%, q=0, IV=40%. The recalculated values are:

- d1 = −0.737948016043253; d2 = −0.852624451859452.
- Call value = $2.906852483315; covered Delta = 0.769726980429.
- Long-call Gamma = 0.013248130655; long-call Vega = 17.422199218145 per 1.0 IV, or $0.174221992181 per one volatility percentage point. Covered-position Gamma and Vega have opposite signs.

At S=$250 with 15/365 remaining and other inputs unchanged: d1=1.642352013277, d2=1.561263527869; call value=$30.890982778487; covered Delta=0.050258536806. The short option's mark-to-market loss is $27.984130295172; the stock gains $50, so the combined change including retained initial premium is about +$22.0158697 before carry and costs. This path changes both price and remaining time. The short-leg loss is not automatically protocol bad debt.

A separate illustrative 14-day, 5%-OTM gross-premium budget equation using assumed annual rates of 8%+1% has a numerical IV root of 18.5424634482%. It is not a closed-form root or a calibrated Spout solvency threshold. Do not substitute those hypothetical rates for documented fees and priority distributions.

The supplied model's 228 checks were rerun; a separate comparison of 27 numbers in the preceding draft found two transcription errors, corrected here. Arithmetic checks are not product tests, a contract audit or a guarantee of financial outcomes. Model limitations include European exercise, assumed volatility, omitted costs in the indicated examples and no validation of actual broker execution.

## Verification summary and tested observations

Authorized access was successfully obtained and live testing was executed on `beta.spout.finance` on Solana Devnet. The live environment verified that testnet token funding works as intended and account balances hydrate accurately. It also confirmed the exact deployment status of routes (`/earn` under construction) and demonstrated the live onboarding deadlock created by backend KYC service errors (`/api/kyc/onboard` HTTP 500, `/api/kyc/session` HTTP 502) paired with Token-2022 Transfer Hook enforcement. Evidence artifacts and visual records have been assembled and preserved for audit.

**Conclusion:** the most valuable next step is a coherent account of shares, cash, debt and exit rights at the user's decision point. This report proposes focused tests and disclosures rather than an unverified redesign of Spout's financial or liquidation engine.

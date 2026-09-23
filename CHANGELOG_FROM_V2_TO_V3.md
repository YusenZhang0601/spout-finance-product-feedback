# Detailed Changelog: V2 to V3 Final Candidate

This document details the exact modifications made in response to the ChatGPT adversarial peer review (Review Grade C: Content Revision Required, feedback points R-01 to R-12).

---

### R-01: Scope Labeling & Elimination of Inflationary Claims
- **Before:** Labeled untested UI suggestions as "Observed Friction" and "CURRENT BORROW DASHBOARD". Claimed "full architecture audit" and "end-to-end teardown".
- **After:** Explicitly demarcated scope in executive summary and all section headers as **"Public-document review + conditional numerical examples + proposed test targets"**. All UI wireframes explicitly labeled as **"Proposed mockup, not a current-app screenshot"**.

### R-02: Correction of Junior Tranche Exit Guidance
- **Before:** Combined exit paths into a generic lender table and erroneously advised queued Junior lenders to take "Instant Exit".
- **After:** Separated Senior and Junior exit routes strictly per Spout's `docs/withdrawals/`. Junior tranche explicitly documented as requiring **minimum 45-day notice**, where queued capital **ceases earning yield but continues bearing loss exposure** and is valued at payout NAV. Instant exit is documented only for Senior reserves.

### R-03: Share Count Attrition vs. Debt Repayment Disentanglement
- **Before:** Claimed that a 100-share position dropping to 48 shares upon assignment ($200 -> $220 strike, $250 stock) represented a "52% options loss" or "equity dilution".
- **After:** Corrected the arithmetic decomposition: of the 52 shares difference, **40 shares equivalent ($10,000 / $250) went to repay principal debt**, and **12 shares equivalent ($100 * $30 / $250) represented upside capped above the strike**. An uncapped position repaying the same debt would retain 60 shares, not 100. Removed the "52% loss" mischaracterization.

### R-04: Rescoping Earnings Cycle Skip Rule
- **Before:** Claimed that Spout's policy of skipping individual-stock option cycles over earnings "completely neutralizes the #1 tail risk".
- **After:** Replaced with accurate risk assessment: skipping earnings cycles reduces scheduled-event options gap risk, but **does not eliminate underlying collateral price drops, macroeconomic shocks, or calendar adjustments**.

### R-05: Oracle Weekend Halt Rules Precision
- **Before:** Generalized Stork oracle off-hours pricing into an asserted "universal 65.5-hour weekend protocol shutdown".
- **After:** Replaced with Spout's exact documented rule: Stork off-hours price feeds operate at reduced frequency, and **stale or unavailable feeds trigger conditional pauses specifically for new borrows and liquidations**, rather than an unconditional protocol-wide halt.

### R-06: Elimination of Unverified Solana CU & TPS Metrics
- **Before:** Stated as an empirical fact that Spout transactions consume 800,000 Compute Units (CU) and yield a fixed 37.5 tx/s ceiling.
- **After:** Removed all speculative throughput claims. Noted that compute budgeting requires transaction traces on deployed programs and separated execution metering from scheduling overhead per Solana official core documentation.

### R-07: Acknowledgement of Existing Protocol Features
- **Before:** Proposed queue position indicators and cycle allocation reports as missing protocol features.
- **After:** Acknowledged that Spout documentation already describes queue position estimation and app distribution views (`docs/withdrawals/` and `docs/settlement-flow/`). Reframed recommendations to focus on auditing and reconciling these existing views.

### R-08: Removal of Unfounded Performance Claims
- **Before:** Claimed that proposed UI changes would achieve ">80% reduction in support tickets" and asserted unverified claims about user psychology.
- **After:** Removed all speculative quantitative benefits and psychological claims. Replaced with objective acceptance criteria: inputs/outputs reconcile without double counting.

### R-09: Date and Calendar Synchronization
- **Before:** Listed `2026-09-26` as Friday (it is Saturday), and stated winner announcement was September 29.
- **After:** Verified all dates: `2026-09-28` is the confirmed winner announcement date (`commitmentDate` in JSON-LD). Verified cycle evaluations without promising rigid Friday 4 PM release times.

### R-10: Black-Scholes Greeks Precision Recalculation
- **Before:** `baseline_d1 = -0.738096`, `postshock_d2 = 1.560946`.
- **After:** Recalculated with arbitrary precision: `baseline_d1 = -0.737948016043253`, `postshock_d2 = 1.561263527869055`. High-precision BSM cross-checks confirmed across 27 quantitative points.

### R-11: Physical Browser Evidence Integration
- **Before:** Screenshot paths referenced in logs without actual PNG files on disk; missing raw JSON-LD.
- **After:** Captured and attached 4 authentic screenshots from live browser session (`superteam_bounty_live.png`, `superteam_submit_modal.png`, `spout_homepage.png`, `spout_beta_gateway.png`), along with raw JSON-LD and Next.js pageProps.

### R-12: CSV Column Escaping & Schema Alignment
- **Before:** `finding_register.csv` had an unescaped comma in F-04 recommendation, producing 10 columns against a 9-column header.
- **After:** Adopted `revised_finding_register.csv` with standard `csv.writer` escaping, 100% compliant with standard `csv.reader`.

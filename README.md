# Spout Finance: Financial Engineering, Protocol Risk & UX Teardown

> **Official Product Feedback & Architecture Teardown Submission**  
> **Platform**: [Superteam Earn](https://superteam.fun/earn/listing/product-feedback-spout-finance/)  
> **Listing ID**: `ae1041af-2378-4a17-b21f-8d74a4505f96`  
> **Target Protocol**: [Spout Finance](https://spout.finance/) (`beta.spout.finance`, Build `v1.0.0 (5d92f4c)`)  
> **Author**: Yusen Zhang ([@Tonypyl](https://x.com/Tonypyl), GitHub: [YusenZhang0601](https://github.com/YusenZhang0601))  
> **Network**: Solana Devnet (`solana:devnet`)  
> **Date**: September 23, 2026  

---

## 🌟 Executive Summary

This repository houses the complete submission dossier, quantitative financial models, and authenticated live testnet diagnostic evidence for the **Spout Finance Product Feedback Bounty** on Superteam Earn. 

My investigation combines **hands-on live Solana Devnet execution** with **rigorous financial engineering analysis**, stress-testing Spout's core proposition: *0% interest borrowing backed by tokenized equities funded through automated covered-call option cycles*.

### Key Milestones Delivered:
1. **Authenticated Live Beta Testing**: Successfully unlocked access (Gate Card No. 241, Passcode [REDACTED]) and funded the Privy embedded wallet on-chain with **20.00 Testnet USDC** via Circle Faucet (Tx: [`3m8SpF6i...`](https://explorer.solana.com/tx/3m8SpF6iKVcVLbDnXxvkgg8QMPjnh2p7f2vRUZjBLDvTS9ni7HGC7jxJ9NpN1hfdt1HWiCvxjHq1FqPiL4hSMf8j?cluster=devnet)).
2. **Reverse-Engineered Onboarding Blocker**: Isolated the exact dual-failure causing live trading lockouts:
   - Backend auto-onboard endpoint (`POST /api/kyc/onboard`) throws unhandled `HTTP 500 Internal Server Error`.
   - Fallback Persona KYC gateway (`POST /api/kyc/session`) fails with `HTTP 502 Bad Gateway` (`persona_unavailable`).
   - Combined with Solana Token-2022 Transfer Hook compliance rules, unverified wallets remain permanently locked out of trade execution ("Verification required").
3. **Mathematical & Econometric Verification**: Developed offline reproducible Black-Scholes-Merton (BSM) and covered-call Delta models passing **228/228 automated unit tests**, independently validating 27 key quantitative assertions.
4. **Sanitized Visual Dossier**: 9 high-resolution evidence screenshots cropped and sanitized to eliminate browser tabs, personal avatars, and system docks.

---

## 📑 Core Findings & Verified Bugs At A Glance

### 🚨 Verified Engineering Blocker (Live Devnet Testing)
| ID | Area | Verified Live Testing Observation | Impact & Engineering Action |
|:---|:---|:---|:---|
| **BUG-01** | Onboarding & KYC API | **Devnet Onboarding Failure (HTTP 500 / 502)**<br>Wallet funded with 20 USDC via Circle Faucet (Tx: `3m8SpF6i...`). `POST /api/kyc/onboard` returns `500 Internal Server Error`, while fallback `POST /api/kyc/session` returns `502 Bad Gateway` (`persona_unavailable`). Order execution remains blocked at "Verification required". | Decouple testnet smart contract evaluation from third-party identity sandbox APIs; deploy an explicit Devnet test-identity issuance route or test-mode bypass to restore full onboarding. |

### 📊 Five Core Product & Financial Architecture Findings
| ID | Domain | Core Architectural Observation | Impact & Engineering Recommendation |
|:---|:---|:---|:---|
| **F-01** | Product Insight | **Restoration of Asset Exposure vs. Shares and Debt**<br>Documented full assignment sells 100 shares at $220 strike ($22,000), repays $10,000 debt, leaving $12,000 cash to repurchase 48 shares at $250. An uncapped sale with the same repayment leaves 60 shares. This is not a "52% wealth loss", but 40 shares repaying principal and 12 shares capped upside. | Before commitment, reconcile original/assigned shares, debt repaid, borrower fee deductions, repurchase price, and remaining debt. Never promise unchanged shares without explaining their funding. |
| **F-02** | User Experience | **Repayment Completion vs. Collateral Availability**<br>Spout's lifecycle permits repayment prior to cycle close, while settlement occurs on Monday 9:00 ET following Friday expiry. Repayment completion and collateral release are distinct events. | Decouple debt state from collateral release state in the UI. Explicitly display release eligibility, cycle calendar, and timezone without promising immediate unlocks the contract cannot deliver. |
| **F-03** | Liquidity & Tranches | **Tranche-Specific Exit Economics & Notice Rights**<br>Senior tranches have documented reserve-backed instant exit (with potential haircut), while Junior requires a minimum 45-day notice during which queued capital ceases earning yield but remains loss-bearing. Inspection of `/earn` confirms vaults are not yet deployed. | Make exit terms tranche-specific in all UI previews. Clarify that queued notice is not a payout guarantee, and separate base redemption from secondary claim resale. |
| **F-04** | Oracle & Risk | **Oracle State Disaggregation & Health Factor Translation**<br>Stork feeds distinguish price status from execution availability and stale-feed pauses. At 50% LTV and 58.8% liquidation threshold, displayed HF=1.18 reflects an exact HF=1.176 with a modeled price cushion of $1 - 0.50/0.588 = 14.97\%$ (not 18%). | Display price freshness, market status, and operation availability separately. Present the true price drop distance to liquidation alongside health factor. |
| **F-05** | Fee & Distribution | **End-to-End Cycle Statement Reconciliation**<br>Cycle accounting spans borrower premium, lender yield, protocol fees, and insurance reserve funding. Net economic outcomes require transparent flow-through. | Provide a unified post-cycle statement reconciling gross premium, debt repayment, fee deductions, and net asset positions without double-counting upside caps. |

---

## 📂 Repository Directory Structure

```text
.
├── README.md                            <- Master project overview & executive teardown
├── submission_report_en.md              <- Comprehensive 5-finding product feedback & analysis report
├── public_teardown_draft_en.md          <- Public-facing teardown thread / article for X & community
├── submission_fields_draft.md           <- Pre-filled copy-paste Superteam submission modal texts
├── BOUNTY_REQUIREMENTS.md               <- Official Superteam bounty specification & rubric (30/25/25/20)
├── CHANGELOG_FROM_V2_TO_V3.md           <- Complete audit trail of revisions and mathematical corrections
├── FINAL_GATE.md                        <- Three-tier readiness gate verification matrix
├── manifest.json                        <- Cryptographic SHA-256 ledger of all 30 repository files
│
├── calculations/                        <- Offline reproducible quantitative financial models
│   ├── audit_model.py                   <- 228/228 math check unit test suite
│   ├── final_numeric_review.py          <- 27-item high-precision BSM & options pricing script
│   ├── final_numeric_review_run.txt     <- Raw execution verification receipt
│   └── numeric_comparisons.csv          <- Term-by-term formula and Greek comparison table
│
└── evidence/                            <- Authentic empirical logs, API traces & visual receipts
    ├── LIVE_BETA_TESTNET_DIAGNOSTIC_EVIDENCE.md <- Full testnet diagnostic report with curl proofs & RPC data
    ├── test_log.csv                     <- 14-item end-to-end test execution ledger
    ├── revised_finding_register.csv     <- Validated 9-column finding register
    ├── screenshot_visual_checks.csv     <- Screenshot audit & sanitization ledger
    ├── source_register.csv              <- Complete documentation, smart contract & web sources
    ├── superteam_next_data.json         <- Raw JSON-LD & Next.js pageProps metadata
    └── screenshots/                     <- 9 sanitized PNG screenshots (2940x1342, cropped)
        ├── superteam_bounty_live.png
        ├── spout_homepage.png
        ├── faucet_usdc_receipt.png
        ├── spout_devnet_verification_failed.png
        ├── spout_buy_verification_required.png
        ├── ask_spout_transfer_hook_kyc.png
        ├── spout_earn_coming_soon.png
        ├── spout_kyc_pending_settings.png
        └── spout_wallet_faucets_modal.png
```

---

## 🔬 Reproducibility & Mathematical Verification

All options formulas, Black-Scholes-Merton Greeks, Delta hedges, and LTV-liquidation cushions are implemented in standalone Python with zero external dependencies (pure standard library `math`):

```bash
# Run the 228-check mathematical model test suite
python3 calculations/audit_model.py

# Run the 27-item high-precision BSM & options comparison review
python3 calculations/final_numeric_review.py
```

---

## 🔗 Key Public Deliverables

1. **Master Report**: [`submission_report_en.md`](submission_report_en.md)
2. **Public Teardown Article**: [`public_teardown_draft_en.md`](public_teardown_draft_en.md)
3. **Testnet Diagnostics Dossier**: [`evidence/LIVE_BETA_TESTNET_DIAGNOSTIC_EVIDENCE.md`](evidence/LIVE_BETA_TESTNET_DIAGNOSTIC_EVIDENCE.md)
4. **On-Chain Solana Devnet Transaction**:
   - Signature: [`3m8SpF6iKVcVLbDnXxvkgg8QMPjnh2p7f2vRUZjBLDvTS9ni7HGC7jxJ9NpN1hfdt1HWiCvxjHq1FqPiL4hSMf8j`](https://explorer.solana.com/tx/3m8SpF6iKVcVLbDnXxvkgg8QMPjnh2p7f2vRUZjBLDvTS9ni7HGC7jxJ9NpN1hfdt1HWiCvxjHq1FqPiL4hSMf8j?cluster=devnet)
   - Recipient (Privy Wallet): `DyPhjzaLx1YBb3hrnuiqrnhmcokLzSQGpowdt912ZFDv`
   - Delivered: `20.00 USDC`

---

## 📜 License & Disclosures

- Author: Yusen Zhang ([@Tonypyl](https://x.com/Tonypyl))
- Purpose: Submission for Superteam Earn Listing `ae1041af-2378-4a17-b21f-8d74a4505f96`.
- Disclaimer: This analysis is for educational and protocol research purposes. It does not constitute financial or investment advice.

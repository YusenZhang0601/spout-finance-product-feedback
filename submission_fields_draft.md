# Superteam Earn Submission Fields — Ready for User Submission

**Listing:** Spout Finance Product Feedback (`ae1041af-2378-4a17-b21f-8d74a4505f96`)  
**URL:** `https://superteam.fun/earn/listing/product-feedback-spout-finance/`  
**Account Handle:** `@Tonypyl` (Display Name: TonyRainforest)  
**Verification Date:** 2026-09-23 01:41:50 UTC  

---

### Field 1: Link to Your Submission
*Label:* `Link to Your Submission`  
*Help text:* "Make sure this link is accessible by everyone!"  
*Target format:* URL (`https://...`)  
*Value to Paste:*
```text
https://github.com/YusenZhang0601/spout-finance-product-feedback/blob/main/submission_report_en.md
```
*(Alternative repository root: https://github.com/YusenZhang0601/spout-finance-product-feedback)*

---

### Field 2: Tweet Link
*Label:* `Tweet Link`  
*Help text:* "This helps sponsors discover (and maybe repost) your work on X! If this submission is for a X thread bounty, you can ignore this field."  
*Target format:* URL (`https://...`)  
*Value to Paste:*
```text
[INSERT_PUBLISHED_TWEET_URL_HERE]
```
*(Recommended: Link to the 1st tweet of your published 10-tweet X thread created from `evidence/10_TWEET_THREAD_DRAFT.md`)*

---

### Field 3: Was there anything about this bounty that was confusing or unclear? Please explain
*Label:* `Was there anything about this bounty that was confusing or unclear? Please explain`  
*Type:* Textarea (Optional feedback question in modal)  
*Text to Paste:*
```text
The bounty description asks participants to test core platform flows and execute testnet transactions. I successfully acquired an official beta access pass (Gate Card No. 241, Passcode [REDACTED]) and logged into beta.spout.finance on Solana Devnet, then funded the wallet with 20 USDC via Circle Faucet (Tx: 3m8SpF6iKVcVLbDnXxvkgg8QMPjnh2p7f2vRUZjBLDvTS9ni7HGC7jxJ9NpN1hfdt1HWiCvxjHq1FqPiL4hSMf8j).

However, live trade execution is currently blocked across the platform because the backend onboarding handler (POST /api/kyc/onboard) returns HTTP 500, and the manual KYC route (POST /api/kyc/session) returns HTTP 502 (persona_unavailable). Combined with the Token-2022 Transfer Hook on spAssets that restricts unverified wallets, order execution is permanently disabled with "Verification required". Providing a working Devnet Mock KYC bypass or documenting this known barrier would greatly streamline testing for all participants.
```

---

### Field 4: Anything Else?
*Label:* `Anything Else?`  
*Type:* Textarea  
*Text to Paste:*
```text
Full submission dossier, live authenticated testnet diagnostics, reproducible numerical models (228/228 verified math checks), and screenshot evidence pack prepared by Yusen Zhang (@Tonypyl). All calculations are reproducible offline via Python (BSM Greeks, covered call delta divergence, and LTV-liquidation cushions). Full evidence dossier, trace logs, and finding registers are attached in the submission.
```

---

### Submission Action
- Button: `Submit using 1 credit` (User account has 3 available credits, expires in ~7 days).
- Notice: "You can edit this submission until the bounty deadline."
- Hard boundary: Agent does NOT perform automated form submissions. Final review and submission button click must be completed by the user.

# 10-Tweet X (Twitter) Thread Draft: Spout Finance Product Feedback

> **Author**: Yusen Zhang ([@Tonypyl](https://x.com/Tonypyl), GitHub: [YusenZhang0601](https://github.com/YusenZhang0601))  
> **Platform**: X (Twitter) Thread (10 Connected Tweets)  
> **Target Accounts**: `@SpoutFi` and `@SuperteamEarn`  
> **Character Constraints**: Standard X post limit ($\le 280$ weighted characters per tweet, URLs count as 23 characters). Verified all 10 tweets $\le 277$ characters.

---

### How to Post on X:
1. Open X and click **Post** (or compose new post).
2. Paste **Tweet 1/10**.
3. Click the **"+" button** at the bottom right of the composer to add the next connected tweet.
4. Paste **Tweet 2/10**, click "+", and repeat through **Tweet 10/10**.
5. *(Optional recommended image)*: Attach screenshot `evidence/screenshots/spout_buy_verification_required.png` to **Tweet 3/10** showing the live Devnet balance and "Verification required" state.
6. Click **Post all** to publish the connected thread in one go.
7. Copy the URL of **Tweet 1** and paste it into Superteam Earn `Tweet Link` field.

---

### Tweet 1/10: Opening Hook & Report Entry
```text
1/10
0% interest is a rate, not the whole cost.

I reviewed @SpoutFi for the @SuperteamEarn bounty: five product lessons and one blocked Devnet journey.

What I tested, what the docs say, and what remains unknown.

Report:
https://github.com/YusenZhang0601/spout-finance-product-feedback/blob/main/submission_report_en.md
```
*(Length: 246 / 280 weighted characters)*

---

### Tweet 2/10: Plain-Language Product Model
```text
2/10
The model: borrow against tokenized stocks; covered-call premiums help fund lenders.

The trade-off: selling calls limits upside without removing stock downside.

Premium received is not net profit. The useful question is what each participant owns, owes and receives.
```
*(Length: 273 / 280 weighted characters)*

---

### Tweet 3/10: Live Testing Boundary & Scope
```text
3/10
In my recorded Sept 23 Devnet session, the app showed 20 test USDC after external faucet funding. Max filled the order amount.

Buy stayed at "Verification required."

I did not complete a stock purchase or loan. Funding a wallet is not a Spout transaction.
```
*(Length: 262 / 280 weighted characters — Recommended: attach sanitized screenshot `spout_buy_verification_required.png`)*

---

### Tweet 4/10: Technical Diagnostics (Without Overstating Root Cause)
```text
4/10
My API notes record:
POST /api/kyc/onboard: 500
POST /api/kyc/session: 502, persona_unavailable

This is an onboarding bug report, not proof of a chain exploit.

The status:null GET came BEFORE both POSTs. Backend root cause and Transfer Hook rejection remain unverified.
```
*(Length: 276 / 280 weighted characters)*

---

### Tweet 5/10: Financial Example F-01 (Share & Debt Recovery)
```text
5/10
F-01: Show shares AND debt.

Hypothetical full assignment: 100 shares sold at $220; repay $10,000; rebuy at $250 = 48 shares.

An uncapped sale with the same repayment leaves 60. Not a 52% wealth loss.

Assumes no fees, premium credits, added cash or new debt.
```
*(Length: 265 / 280 weighted characters)*

---

### Tweet 6/10: Repayment & Collateral Release F-02
```text
6/10
F-02: "Debt repaid" is not "collateral available."

Spout's docs distinguish repayment, cycle close and settlement.

Show separate debt and collateral states, with actual release eligibility and timezone. Do not promise an immediate unlock the product cannot deliver.
```
*(Length: 272 / 280 weighted characters)*

---

### Tweet 7/10: Lender Exit Terms F-03
```text
7/10
F-03: Make exit terms tranche-specific.

The docs give Junior a minimum 45-day notice. Queued Junior capital stops earning yield but remains loss-bearing until payment.

Notice is not a payout-date guarantee. Earn was unavailable in my session; I did not test withdrawals.
```
*(Length: 277 / 280 weighted characters)*

---

### Tweet 8/10: Health Factor & Price Cushion F-04
```text
8/10
F-04: Explain the health factor.

At 50% LTV and a 58.8% liquidation threshold:
HF = 1.176, displayed as 1.18.
Modeled price cushion = 1 - 0.50/0.588 = 14.966%, not 18%.

Assumes fixed debt, shares and threshold. Show price freshness and operation status separately.
```
*(Length: 271 / 280 weighted characters)*

---

### Tweet 9/10: Cycle Statement & Fee Reconciliation F-05
```text
9/10
F-05: Make the existing cycle statement reconcile.

Who receives premium? What pays debt? Which fees apply? What reaches insurance and lenders?

Track shares, cash, debt and option obligations. Do not count capped upside again as a separate cash loss.
```
*(Length: 256 / 280 weighted characters)*

---

### Tweet 10/10: Priorities, Links & Independent Disclosure
```text
10/10
First, restore the supported onboarding path without weakening identity checks.

Then make shares, cash, debt and exit rights clear before commitment.

Report, bug notes and code:
https://github.com/YusenZhang0601/spout-finance-product-feedback

Independent bounty entry. AI-assisted review; not a mainnet audit.
```
*(Length: 277 / 280 weighted characters)*

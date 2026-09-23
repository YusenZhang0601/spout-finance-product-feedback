# What does 0% stock-backed borrowing actually cost?
## Five questions to make Spout's documented model easier to understand

**Author:** Yusen Zhang ([@Tonypyl](https://x.com/Tonypyl)) · September 23, 2026  
**Format:** Public Teardown / X (Twitter) Long-Form Thread Candidate  

> **Disclosure:** Access was verified on the live Spout Beta portal (`beta.spout.finance`, Build `v1.0.0 (5d92f4c)`) on Solana Devnet, including on-chain testnet USDC funding and UI inspection. The economic examples below are hypothetical walkthroughs, and technical diagnostics reflect observed backend and UI behavior in the testnet environment.

Spout describes borrowing stablecoins against tokenized stock collateral without ongoing interest. A covered-call strategy supplies option premium. That changes the economic exchange; it does not make financing free of all costs or risks. [Borrowing](https://spout.finance/docs/how-borrowing-works/)

## 1. Show shares and debt together after assignment

The documented assignment route sells assigned shares, repays debt and can repurchase the same asset with remaining cash. [Assignment](https://spout.finance/docs/options-assignment/)

Suppose all 100 shares are assigned at $220, debt is $10,000 and the repurchase price is $250. With no fees, premium credits, added cash or new borrowing, $22,000 less $10,000 buys 48 shares.

That is **not a 52% investment loss**. Forty shares' worth paid back principal; twelve shares' worth reflects upside above the strike. Selling an uncapped position at $250 and repaying the same debt would leave 60 shares. The useful preview shows every share, cash and debt transition—not a frightening percentage without its denominator.

## 2. Separate “debt repaid” from “collateral available”

The borrowing and settlement documents describe distinct cycle events. A confirmation page should tell the user what repayment has completed, what remains active and when collateral actually becomes available. A fixed Friday unlock timer should not be invented from a description of Friday option expiry. [Borrowing](https://spout.finance/docs/how-borrowing-works/) · [Settlement](https://spout.finance/docs/settlement-flow/)

## 3. Explain the exit route for the selected tranche

Junior's minimum 45-day notice is different from Senior's reserve-based instant exit. Queue entry stops yield, while Junior continues to bear losses until payment. Selling a queued claim is a separate transaction with a buyer. The base withdrawal fee and any instant-exit haircut also need separate labels. [Withdrawals](https://spout.finance/docs/withdrawals/) · [Fees](https://spout.finance/docs/fee-structure/)

A notice period should not be mistaken for a guaranteed payout date. The docs already describe queue information; the next task is to test the existing flow.

## 4. Translate health factor without changing its meaning

With initial LTV=50% and liquidation threshold=58.8%, exact HF=1.176, displayed about 1.18. Assuming debt, shares and threshold stay fixed, the modeled price decline to the boundary is `1 − 0.50/0.588 = 14.966%`—not 18%. The calculation must use unrounded values. [Liquidation Example](https://spout.finance/docs/liquidation-example/)

Price freshness, execution availability and settlement are also different states. The oracle page describes off-hours updates and conditional pauses, not proof of an automatic shutdown for every hour of the weekend. [Oracles](https://spout.finance/docs/oracles/)

## 5. Make one cycle ledger answer who gets paid and who bears each cost

Different pages discuss borrower premium, lender allocation and assignment from different perspectives. The existing distribution view should reconcile these amounts and explain fee bases and insurance allocations without double-counting. [Strike Selection](https://spout.finance/docs/strike-selection/) · [Settlement](https://spout.finance/docs/settlement-flow/)

Spout also documents skipping option cycles over individual-stock earnings. That is a useful scheduled-event control, not the removal of all collateral gap risk or proof of implementation. [Lifecycle](https://spout.finance/docs/borrowing-lifecycle/)

## The product improvement

Before commitment, show what the user will own, owe, receive and still be exposed to under each outcome. Then make the actual cycle statement reconcile to that preview. No claimed reduction in support tickets or guarantee of lender returns is needed to explain why that clarity matters.

A separately prepared technical report, live testnet diagnostics, and offline calculation files support the examples. Their public links must be added only after publication and access checks; no deployed mainnet audit is implied.

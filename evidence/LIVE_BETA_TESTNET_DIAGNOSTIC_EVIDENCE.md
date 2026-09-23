# Spout Finance Live Beta Testnet Diagnostic Evidence Dossier

> **Inspection Date**: 2026-09-23 (UTC)  
> **Target Application**: Spout Finance Beta (`https://beta.spout.finance`)  
> **Build Version**: `v1.0.0 (5d92f4c)`  
> **Network Cluster**: Solana Devnet (`solana:devnet`)  
> **Tester Embedded Wallet**: `DyPhjzaLx1YBb3hrnuiqrnhmcokLzSQGpowdt912ZFDv` (Privy Auth Provider)  
> **Access Pass ID**: Gate Access Card No. 241 (Passcode [REDACTED])

---

## 1. Executive Summary of Diagnostic Findings

During hands-on live testing of the authenticated Spout Finance Devnet application, I conducted testing covering wallet provisioning, faucet funding, stock trading (Buy/Sell), leverage selection, collateral borrowing, and earning vaults. 

My investigation successfully funded the account on-chain with 20.00 Testnet USDC, but uncovered a critical onboarding deadlock preventing transaction execution across the tested environment. Through frontend inspection and authenticated API tracing, I isolated the dual-failure behavior on Spout's backend infrastructure:

1. **Devnet Auto-Onboard Crash (`POST /api/kyc/onboard`)**: Returned `HTTP 500 Internal Server Error`, triggering the UI warning banner `"Devnet verification failed for this wallet — you can browse, but buying stays locked. Reconnect to retry."`
2. **Third-Party KYC Gateway Failure (`POST /api/kyc/session`)**: Returned `HTTP 502 Bad Gateway` with upstream error `"persona_unavailable"`, indicating that the Persona sandbox integration is unreachable.
3. **Contract-Level Lockout (Solana Token-2022 Transfer Hook)**: Because both backend verification paths fail, the wallet remains `status: null`. The `spAssets` Token-2022 Transfer Hook programmatically rejects all unverified token transfers, locking the Buy button in a disabled `Verification required` state.
4. **Earn Vault Incompleteness**: The `/earn` route physically renders `"Earn is coming soon — Lending vaults are on the way"`, verifying that lending vault contracts are not yet deployed in this build.

---

## 2. On-Chain Testnet Faucet Evidence

### 2.1 USDC Funding Transaction
- **Asset**: Circle Testnet USDC (Mint: `4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU`)
- **Recipient Address**: `DyPhjzaLx1YBb3hrnuiqrnhmcokLzSQGpowdt912ZFDv`
- **Associated Token Account**: `D3NGdAGLXNxhRBnZejGxJUpZMTJBk5ukhJo7DacewaH4`
- **Amount Delivered**: `20,000,000` base units (**20.00 USDC**)
- **Transaction Signature**: `3m8SpF6iKVcVLbDnXxvkgg8QMPjnh2p7f2vRUZjBLDvTS9ni7HGC7jxJ9NpN1hfdt1HWiCvxjHq1FqPiL4hSMf8j`
- **Solana Devnet Block Explorer Link**: [View on Solana Explorer](https://explorer.solana.com/tx/3m8SpF6iKVcVLbDnXxvkgg8QMPjnh2p7f2vRUZjBLDvTS9ni7HGC7jxJ9NpN1hfdt1HWiCvxjHq1FqPiL4hSMf8j?cluster=devnet)
- **Visual Receipt**: Captured at `evidence/screenshots/faucet_usdc_receipt.png`.

```json
{
  "jsonrpc": "2.0",
  "result": {
    "context": { "apiVersion": "4.3.0-rc.0", "slot": 502855730 },
    "value": [
      {
        "account": {
          "data": {
            "parsed": {
              "info": {
                "isNative": false,
                "mint": "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU",
                "owner": "DyPhjzaLx1YBb3hrnuiqrnhmcokLzSQGpowdt912ZFDv",
                "state": "initialized",
                "tokenAmount": {
                  "amount": "20000000",
                  "decimals": 6,
                  "uiAmount": 20.0,
                  "uiAmountString": "20"
                }
              },
              "type": "account"
            },
            "program": "spl-token",
            "space": 165
          },
          "executable": false,
          "lamports": 1488440,
          "owner": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
          "pubkey": "D3NGdAGLXNxhRBnZejGxJUpZMTJBk5ukhJo7DacewaH4"
        }
      }
    ]
  },
  "id": 1
}
```

---

## 3. Live UI Interaction & Friction Telemetry

### 3.1 Balance & State Hydration
Upon receiving the test USDC, the platform header immediately synchronized the balance, displaying `$20 USDC`.

### 3.2 Order Entry & Deadlock
- **Target Asset**: NVIDIA Corporation (`NVDA`), Apple Inc. (`AAPL`).
- **Input Interaction**: Clicking the `Max` button correctly bound the available balance, auto-filling `$20` into the USD amount field.
- **Computed Outputs**: The widget accurately calculated estimated shares (`0.08 NVDA`), today's cost (`$20.00`), and displayed the leverage slider (1.0x - 2.0x).
- **Execution Block**: The primary action button was persistently disabled with text `Verification required`.
- **Warning Toast**: A top-banner alert explicitly rendered:
  > *"Devnet verification failed for this wallet — you can browse, but buying stays locked. Reconnect to retry."*
- **Visual Evidence**: Captured at `evidence/screenshots/spout_devnet_verification_failed.png` and `evidence/screenshots/spout_buy_verification_required.png`.

---

## 4. Backend API Network Trace & Root-Cause Deconstruction

Using the authenticated Privy session Bearer token, we performed direct HTTP/2 probes against all three identity endpoints defined in Spout's frontend bundles (`2_2812ys4d3sr.js` and `2_j79jql31nfu.js`):

### 4.1 Endpoint 1: Devnet Auto-Onboarding (`POST /api/kyc/onboard`)
```http
POST /api/kyc/onboard HTTP/2
Host: beta.spout.finance
Authorization: Bearer eyJhbGciOiJFUzI1Ni...
Content-Type: application/json

{"walletAddress":"DyPhjzaLx1YBb3hrnuiqrnhmcokLzSQGpowdt912ZFDv"}

--- RESPONSE ---
HTTP/2 500 Internal Server Error
Content-Type: application/json
Date: Wed, 23 Sep 2026 08:43:37 GMT
Server: CloudFront
Via: 1.1 9c9006ad97c90bc44f681bfa89d2c84e.cloudfront.net (CloudFront)
X-Amz-Cf-Id: DCdq6SIY6lD8UNIMAJgy2OdZ5JxeRWqFbE2RkUY2bRxBtjIuVy8UIg==

{"error":"Internal server error"}
```
**Diagnostic Conclusion**: The automated handler meant to provision mock identity records for Devnet users crashed internally, failing to issue on-chain verification.

### 4.2 Endpoint 2: Persona KYC Session (`POST /api/kyc/session`)
```http
POST /api/kyc/session HTTP/2
Host: beta.spout.finance
Authorization: Bearer eyJhbGciOiJFUzI1Ni...
Content-Type: application/json

{"address":"DyPhjzaLx1YBb3hrnuiqrnhmcokLzSQGpowdt912ZFDv"}

--- RESPONSE ---
HTTP/2 502 Bad Gateway
Content-Type: application/json
Date: Wed, 23 Sep 2026 08:43:34 GMT
Server: CloudFront
Via: 1.1 cf0358efeeb32c222cf57420ce241ce8.cloudfront.net (CloudFront)
X-Amz-Cf-Id: S76agfWzUzLI8DxutCumR8rKp9TJIm_K09A-boJhrw_PJONkz2z-yQ==

{
  "error": "persona_unavailable",
  "message": "Persona could not be reached. Nothing was lost.",
  "upstream": { "error": "persona_unavailable" }
}
```
**Diagnostic Conclusion**: The fallback manual verification service failed because Spout's backend could not communicate with Persona's upstream API sandbox.

### 4.3 Endpoint 3: KYC Status Query (`GET /api/kyc/status`)
```http
GET /api/kyc/status?address=DyPhjzaLx1YBb3hrnuiqrnhmcokLzSQGpowdt912ZFDv HTTP/2
Host: beta.spout.finance
Authorization: Bearer eyJhbGciOiJFUzI1Ni...

--- RESPONSE ---
HTTP/2 200 OK
Content-Type: application/json
Date: Wed, 23 Sep 2026 08:43:33 GMT

{"status":null}
```
**Diagnostic Conclusion**: Because both endpoints 4.1 and 4.2 failed, status remains `null`, preventing the account state from transitioning to `approved`.

---

## 5. Token-2022 Transfer Hook Enforcement

Spout's built-in AI assistant ("Ask Spout") confirmed the underlying smart-contract architectural invariant:

> *"spAssets use Token-2022 with a transfer hook, meaning unverified wallets cannot hold or transfer them. You will need to verify your identity before you can hold spAssets or participate in lending. The platform is open to anyone who passes KYC."*
> *(Evidence: `evidence/screenshots/ask_spout_transfer_hook_kyc.png`)*

### Architectural Implications
While the Token-2022 Transfer Hook is an exceptional design choice for production regulatory compliance (ensuring only KYC-verified addresses can hold equity-backed tokens), its enforcement in Devnet without a working Mock Identity provider creates a **universal blocker**. Testers cannot mint `spAssets`, which cascades into:
- Inability to test collateral locking.
- Inability to draw 0% interest loans against stocks.
- Inability to test margin health factor degradation or liquidation workflows.

---

## 6. Route Completeness Matrix

| Route | UI Status | Functional State | Evidence Path |
| :--- | :--- | :--- | :--- |
| `/buy` (Trade) | Fully rendered, real-time market countdown (5h) | Disabled (`Verification required`) due to KYC failure | `spout_buy_verification_required.png` |
| `/borrow` | Empty state | Blocked: requires holding `spAssets` collateral | `spout_beta_borrow.png` |
| `/earn` | Placeholder | Under construction: *"Earn is coming soon — Lending vaults are on the way"* | `spout_earn_coming_soon.png` |
| `/settings` | Profile loaded | Stuck: `KYC Status: Verification pending — no identity on-chain yet: Pending` | `spout_kyc_pending_settings.png` |

---

## 7. Concrete Recommendations for the Spout Engineering Team

1. **Implement a Devnet Bypass / Mock Identity Claim**:
   - For `solana:devnet`, introduce a direct client-side Mock Identity transaction or patch `/api/kyc/onboard` to sign and record a mock verified status without external dependencies.
2. **Add Persona Sandbox Circuit Breaker**:
   - Catch upstream 502 errors from Persona and gracefully fall back to a manual devnet test bypass with an explicit UI toggle ("Bypass KYC for Devnet Testing").
3. **Decouple Transfer Hook Enforcement on Devnet**:
   - In the devnet deployment of the `spAsset` Token-2022 mints, configure the transfer hook to allow transfers to addresses holding testnet devnet SOL, unlocking community test coverage for borrowing and liquidation mechanics.


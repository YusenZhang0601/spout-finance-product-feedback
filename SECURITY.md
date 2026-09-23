# Security & Responsible Disclosure Policy

## 1. Scope & Credentials Sanitization
This repository contains product feedback, financial architecture models, and testnet diagnostics for **Spout Finance** on **Solana Devnet**.

- **No Production Secrets**: No mainnet private keys, seed phrases, production passwords, or sensitive credentials are stored or tracked in this repository.
- **Testnet Credentials Redacted**: All Devnet access passcodes, OAuth callback parameters (`privy_oauth_state`, `privy_oauth_code`), and internal session tokens have been physically redacted (`[REDACTED]`).
- **Devnet Test Wallets**: The embedded wallet used for testing (`DyPhjzaLx1YBb3hrnuiqrnhmcokLzSQGpowdt912ZFDv`) is a disposable testnet key funded exclusively with Devnet faucet tokens (Circle Devnet USDC and Solana Devnet SOL).
- **Git History Hygiene**: Git history has been sanitized and squashed to prevent historical retention of un-redacted test credentials or transient tokens.

## 2. Reporting Vulnerabilities
If you identify any security vulnerability or exposed credentials in this repository, please report it immediately:
- **Author**: Yusen Zhang ([@Tonypyl](https://x.com/Tonypyl) on X / GitHub: [YusenZhang0601](https://github.com/YusenZhang0601))
- **Email**: `zhangyswx@163.com`

For protocol-level vulnerabilities in Spout Finance, please contact the Spout Finance team directly via official channels (`security@spout.finance` or official community/Telegram links).

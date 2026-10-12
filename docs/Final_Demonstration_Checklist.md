# CertiChain — Final Demonstration Checklist

Use this checklist while preparing the college submission. Check items only after you have personally completed them.

## Build and deployment
- [ ] Opened `contracts/CertiChain.sol` in Remix.
- [ ] Compiled with Solidity 0.8.24 or compatible 0.8.x.
- [ ] Deployed to Remix VM or Ganache.
- [ ] Saved the network name and deployed contract address.
- [ ] Started the browser interface from `app/` and connected the wallet to the same network.

## Demonstration cases
- [ ] Verify an unknown fingerprint.
- [ ] Issue a sample fingerprint from the authorized account.
- [ ] Verify that the issued fingerprint is valid.
- [ ] Attempt duplicate issuance and record the revert.
- [ ] Revoke the issued fingerprint.
- [ ] Verify that it exists but is no longer valid.
- [ ] Attempt issuance from an unauthorized account and record the revert.

## Evidence to capture
- [ ] Remix compiler success.
- [ ] Deployment address.
- [ ] Issue transaction output/hash.
- [ ] Valid verification output.
- [ ] Revoke transaction output/hash.
- [ ] Revoked verification output.
- [ ] Unauthorized access test output.

Save genuine screenshots in `docs/screenshots/`. Never claim a test passed until it has been run. Do not use real student documents or personal information in demo files.

## Final submission check
- [ ] README includes introduction, problem, objectives, tools, architecture, contract design, setup, test plan, conclusion, and future scope.
- [ ] Source contract is in `contracts/CertiChain.sol`.
- [ ] Report PDF contains the required sections.
- [ ] Screenshots and actual sample transaction details are included.
- [ ] Repository URL opens correctly.

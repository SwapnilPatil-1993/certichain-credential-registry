import { BrowserProvider, Contract, isAddress, isHexString } from "https://cdn.jsdelivr.net/npm/ethers@6.17.0/+esm";

const ABI = [
  "function owner() view returns (address)",
  "function authorizedIssuer(address) view returns (bool)",
  "function issueCertificate(bytes32 certificateHash)",
  "function revokeCertificate(bytes32 certificateHash)",
  "function verifyCertificate(bytes32 certificateHash) view returns (bool exists, bool valid, address issuer, uint64 issuedAt)"
];
const ADDRESS_KEY = "certichain.registryAddress";
const $ = (id) => document.getElementById(id);
let provider;
let signer;
let account = "";
let canIssue = false;
let canRevoke = false;
let toastTimer;

function shortAddress(value) { return value ? `${value.slice(0, 6)}…${value.slice(-4)}` : ""; }
function hashIsValid(value) { return isHexString(value.trim(), 32); }
function contractAddress() { return $("contractAddress").value.trim(); }
function toast(message) {
  const node = $("toast"); node.textContent = message; node.classList.add("show");
  clearTimeout(toastTimer); toastTimer = setTimeout(() => node.classList.remove("show"), 3600);
}
function showTx(message, kind = "") {
  $("txResult").textContent = message;
  $("txResult").style.color = kind === "error" ? "#ffb8a9" : kind === "success" ? "#9debd2" : "#aab8c1";
}
async function refreshAccess() {
  const badge = $("issuerAccess");
  canIssue = false; canRevoke = false;
  if (!account || !isAddress(contractAddress())) {
    badge.textContent = "● Wallet not checked";
    $("issue").disabled = true; $("revoke").disabled = true;
    return;
  }
  try {
    const read = new Contract(contractAddress(), ABI, provider);
    canIssue = await read.authorizedIssuer(account);
    const owner = await read.owner();
    canRevoke = canIssue || owner.toLowerCase() === account.toLowerCase();
    badge.textContent = canIssue ? "● Authorized issuer" : canRevoke ? "● Registry owner" : "● Read-only wallet";
    $("registry").textContent = shortAddress(contractAddress());
  } catch {
    badge.textContent = "● Registry unavailable";
    $("registry").textContent = "Check address / network";
  }
  const hasHash = hashIsValid($("hashInput").value);
  $("issue").disabled = !canIssue || !hasHash;
  $("revoke").disabled = !canRevoke || !hasHash;
}
async function connectWallet() {
  if (!window.ethereum) return toast("No injected wallet found. Install a browser wallet to use the registry.");
  try {
    provider = new BrowserProvider(window.ethereum);
    await provider.send("eth_requestAccounts", []);
    signer = await provider.getSigner(); account = await signer.getAddress();
    const network = await provider.getNetwork();
    $("network").textContent = `${network.name === "unknown" ? "EVM" : network.name} · ${network.chainId}`;
    $("account").textContent = shortAddress(account);
    $("connect").innerHTML = `${shortAddress(account)} <span>✓</span>`;
    await refreshAccess();
    toast("Wallet connected. Confirm the network and registry address before sending a transaction.");
  } catch (error) { toast(error.shortMessage || error.message || "Wallet connection was not completed."); }
}
async function fingerprint(file) {
  const data = await crypto.subtle.digest("SHA-256", await file.arrayBuffer());
  return `0x${Array.from(new Uint8Array(data), (x) => x.toString(16).padStart(2, "0")).join("")}`;
}
async function useFile(file) {
  if (!file) return;
  $("filename").textContent = file.name; $("digest").textContent = "Calculating…";
  try {
    const hash = await fingerprint(file);
    $("digest").textContent = hash; $("hashInput").value = hash;
    $("verifyButton").disabled = false;
    $("verifyResult").className = "result";
    $("verifyResult").textContent = "Fingerprint ready. Verify it against the configured registry.";
    await refreshAccess();
  } catch (error) { $("digest").textContent = "Could not read this file"; toast(error.message || "File fingerprinting failed."); }
}
async function verify() {
  const hash = $("hashInput").value.trim();
  const result = $("verifyResult");
  if (!hashIsValid(hash)) return toast("Choose a file or paste a valid 32-byte fingerprint first.");
  if (!isAddress(contractAddress())) return toast("Add a deployed registry address in Developer Configuration first.");
  if (!provider) return toast("Connect a wallet so the app can read the selected EVM network.");
  result.className = "result"; result.textContent = "Checking the registry…";
  try {
    const [exists, valid, issuer, issuedAt] = await new Contract(contractAddress(), ABI, provider).verifyCertificate(hash);
    if (!exists) { result.className = "result invalid"; result.textContent = "No record found for this fingerprint in the selected contract."; return; }
    result.className = valid ? "result success" : "result warning";
    result.textContent = `${valid ? "Valid record" : "Revoked record"} · Issuer ${shortAddress(issuer)} · Issued ${new Date(Number(issuedAt) * 1000).toLocaleString()}`;
  } catch (error) {
    result.className = "result warning";
    result.textContent = error.shortMessage || error.message || "Registry query failed. Check the network and contract address.";
  }
}
async function transact(method) {
  const hash = $("hashInput").value.trim();
  if (!hashIsValid(hash)) return toast("Choose a file or paste a valid 32-byte fingerprint first.");
  if (!signer || !isAddress(contractAddress())) return toast("Connect a wallet and enter a valid registry address first.");
  try {
    const contract = new Contract(contractAddress(), ABI, signer);
    showTx("Confirm the transaction in your wallet…");
    $("issue").disabled = true; $("revoke").disabled = true;
    const tx = await contract[method](hash);
    showTx(`Submitted: ${tx.hash}`);
    const receipt = await tx.wait();
    showTx(`${method === "issueCertificate" ? "Issuance" : "Revocation"} confirmed in block ${receipt.blockNumber}. Transaction: ${tx.hash}`, "success");
    toast("Transaction confirmed on the selected network.");
    if (method === "issueCertificate") await verify();
  } catch (error) { showTx(error.shortMessage || error.reason || error.message || "Transaction failed.", "error"); }
  finally { await refreshAccess(); }
}

$("connect").addEventListener("click", connectWallet);
$("file").addEventListener("change", (event) => useFile(event.target.files?.[0]));
$("drop").addEventListener("dragover", (event) => { event.preventDefault(); $("drop").style.borderColor = "#25b699"; });
$("drop").addEventListener("dragleave", () => { $("drop").style.borderColor = ""; });
$("drop").addEventListener("drop", (event) => { event.preventDefault(); useFile(event.dataTransfer.files?.[0]); });
$("verifyButton").addEventListener("click", verify);
$("copy").addEventListener("click", async () => {
  const hash = $("digest").textContent;
  if (!hashIsValid(hash)) return toast("There is no fingerprint to copy yet.");
  await navigator.clipboard.writeText(hash); toast("Fingerprint copied.");
});
$("hashInput").addEventListener("input", () => {
  const hasHash = hashIsValid($("hashInput").value);
  $("verifyButton").disabled = !hasHash;
  $("issue").disabled = !canIssue || !hasHash;
  $("revoke").disabled = !canRevoke || !hasHash;
});
$("saveAddress").addEventListener("click", async () => {
  const address = contractAddress();
  if (!isAddress(address)) return toast("Enter a valid EVM contract address.");
  localStorage.setItem(ADDRESS_KEY, address); $("registry").textContent = shortAddress(address);
  toast("Registry address saved in this browser."); await refreshAccess();
});
if (window.ethereum) {
  window.ethereum.on?.("accountsChanged", () => window.location.reload());
  window.ethereum.on?.("chainChanged", () => window.location.reload());
}
const savedAddress = localStorage.getItem(ADDRESS_KEY);
if (savedAddress && isAddress(savedAddress)) { $("contractAddress").value = savedAddress; $("registry").textContent = shortAddress(savedAddress); }


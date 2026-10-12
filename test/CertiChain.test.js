const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CertiChain", function () {
  async function deployFixture() {
    const [owner, issuer, stranger] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("CertiChain");
    const certiChain = await Factory.deploy();
    await certiChain.waitForDeployment();
    return { certiChain, owner, issuer, stranger };
  }

  const sampleHash = (label) => ethers.sha256(ethers.toUtf8Bytes(label));

  it("sets the deployer as owner and initial authorized issuer", async function () {
    const { certiChain, owner } = await deployFixture();
    expect(await certiChain.owner()).to.equal(owner.address);
    expect(await certiChain.authorizedIssuer(owner.address)).to.equal(true);
  });

  it("allows owner to authorize an issuer and rejects non-owner administration", async function () {
    const { certiChain, owner, issuer, stranger } = await deployFixture();
    await expect(certiChain.connect(owner).setIssuerAuthorization(issuer.address, true))
      .to.emit(certiChain, "IssuerAuthorizationChanged")
      .withArgs(issuer.address, true);
    expect(await certiChain.authorizedIssuer(issuer.address)).to.equal(true);
    await expect(certiChain.connect(stranger).setIssuerAuthorization(issuer.address, false))
      .to.be.revertedWith("CertiChain: caller is not owner");
  });

  it("issues a fingerprint and returns a valid verification record", async function () {
    const { certiChain, owner } = await deployFixture();
    const hash = sampleHash("sample-certificate-001");
    await expect(certiChain.connect(owner).issueCertificate(hash))
      .to.emit(certiChain, "CertificateIssued");
    const result = await certiChain.verifyCertificate(hash);
    expect(result.exists).to.equal(true);
    expect(result.valid).to.equal(true);
    expect(result.issuer).to.equal(owner.address);
    expect(result.issuedAt).to.be.greaterThan(0);
  });

  it("rejects duplicate and zero-hash issuance", async function () {
    const { certiChain, owner } = await deployFixture();
    const hash = sampleHash("sample-certificate-duplicate");
    await certiChain.connect(owner).issueCertificate(hash);
    await expect(certiChain.connect(owner).issueCertificate(hash))
      .to.be.revertedWith("CertiChain: already issued");
    await expect(certiChain.connect(owner).issueCertificate(ethers.ZeroHash))
      .to.be.revertedWith("CertiChain: empty hash");
  });

  it("rejects issuance from an unauthorized account", async function () {
    const { certiChain, stranger } = await deployFixture();
    await expect(certiChain.connect(stranger).issueCertificate(sampleHash("unauthorized")))
      .to.be.revertedWith("CertiChain: caller is not authorized");
  });

  it("allows the issuer to revoke while preserving the record", async function () {
    const { certiChain, owner } = await deployFixture();
    const hash = sampleHash("sample-certificate-revoke");
    await certiChain.connect(owner).issueCertificate(hash);
    await expect(certiChain.connect(owner).revokeCertificate(hash))
      .to.emit(certiChain, "CertificateRevoked");
    const result = await certiChain.verifyCertificate(hash);
    expect(result.exists).to.equal(true);
    expect(result.valid).to.equal(false);
  });

  it("rejects revocation by an unrelated account and repeated revocation", async function () {
    const { certiChain, owner, stranger } = await deployFixture();
    const hash = sampleHash("sample-certificate-access-control");
    await certiChain.connect(owner).issueCertificate(hash);
    await expect(certiChain.connect(stranger).revokeCertificate(hash))
      .to.be.revertedWith("CertiChain: not issuer or owner");
    await certiChain.connect(owner).revokeCertificate(hash);
    await expect(certiChain.connect(owner).revokeCertificate(hash))
      .to.be.revertedWith("CertiChain: already revoked");
  });

  it("rejects revocation of an unknown fingerprint", async function () {
    const { certiChain, owner } = await deployFixture();
    await expect(certiChain.connect(owner).revokeCertificate(sampleHash("unknown")))
      .to.be.revertedWith("CertiChain: unknown certificate");
  });
});
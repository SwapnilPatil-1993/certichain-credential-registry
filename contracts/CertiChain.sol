// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title CertiChain - minimal on-chain academic certificate registry
/// @notice Stores certificate fingerprints and issuer/revocation state, never personal student data.
contract CertiChain {
    address public owner;

    struct Certificate {
        address issuer;
        uint64 issuedAt;
        bool revoked;
        bool exists;
    }

    mapping(address => bool) public authorizedIssuer;
    mapping(bytes32 => Certificate) private certificates;

    event IssuerAuthorizationChanged(address indexed issuer, bool authorized);
    event CertificateIssued(bytes32 indexed certificateHash, address indexed issuer, uint64 issuedAt);
    event CertificateRevoked(bytes32 indexed certificateHash, address indexed issuer, uint64 revokedAt);

    modifier onlyOwner() {
        require(msg.sender == owner, "CertiChain: caller is not owner");
        _;
    }

    modifier onlyIssuer() {
        require(authorizedIssuer[msg.sender], "CertiChain: caller is not authorized");
        _;
    }

    constructor() {
        owner = msg.sender;
        authorizedIssuer[msg.sender] = true;
        emit IssuerAuthorizationChanged(msg.sender, true);
    }

    function setIssuerAuthorization(address issuer, bool authorized) external onlyOwner {
        require(issuer != address(0), "CertiChain: zero address");
        authorizedIssuer[issuer] = authorized;
        emit IssuerAuthorizationChanged(issuer, authorized);
    }

    /// @dev certificateHash is the SHA-256 digest of a canonical certificate file, computed off-chain.
    function issueCertificate(bytes32 certificateHash) external onlyIssuer {
        require(certificateHash != bytes32(0), "CertiChain: empty hash");
        require(!certificates[certificateHash].exists, "CertiChain: already issued");
        uint64 issuedAt = uint64(block.timestamp);
        certificates[certificateHash] = Certificate(msg.sender, issuedAt, false, true);
        emit CertificateIssued(certificateHash, msg.sender, issuedAt);
    }

    function revokeCertificate(bytes32 certificateHash) external {
        Certificate storage certificate = certificates[certificateHash];
        require(certificate.exists, "CertiChain: unknown certificate");
        require(msg.sender == owner || msg.sender == certificate.issuer, "CertiChain: not issuer or owner");
        require(!certificate.revoked, "CertiChain: already revoked");
        certificate.revoked = true;
        emit CertificateRevoked(certificateHash, msg.sender, uint64(block.timestamp));
    }

    /// @return exists Whether the hash has ever been issued.
    /// @return valid Whether it exists and has not been revoked.
    /// @return issuer Address that issued it.
    /// @return issuedAt Timestamp recorded at issuance (Unix seconds).
    function verifyCertificate(bytes32 certificateHash)
        external view returns (bool exists, bool valid, address issuer, uint64 issuedAt)
    {
        Certificate memory certificate = certificates[certificateHash];
        return (certificate.exists, certificate.exists && !certificate.revoked, certificate.issuer, certificate.issuedAt);
    }
}



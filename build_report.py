from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus.flowables import Flowable
from pathlib import Path

OUT = Path(__file__).parent / 'docs' / 'Project_Report.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
NAVY = colors.HexColor('#10243A')
BLUE = colors.HexColor('#176B87')
TEAL = colors.HexColor('#35B8A6')
PALE = colors.HexColor('#EAF3F6')
INK = colors.HexColor('#203040')
GREY = colors.HexColor('#5F6F7C')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='CoverTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=29, leading=34, textColor=NAVY, alignment=TA_LEFT, spaceAfter=12))
styles.add(ParagraphStyle(name='CoverSub', parent=styles['Normal'], fontSize=13, leading=19, textColor=BLUE, spaceAfter=12))
styles.add(ParagraphStyle(name='H1x', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=17, leading=22, textColor=NAVY, spaceBefore=4, spaceAfter=10))
styles.add(ParagraphStyle(name='H2x', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=BLUE, spaceBefore=8, spaceAfter=5))
styles.add(ParagraphStyle(name='Bodyx', parent=styles['BodyText'], fontName='Helvetica', fontSize=9.3, leading=14, textColor=INK, spaceAfter=7))
styles.add(ParagraphStyle(name='Smallx', parent=styles['BodyText'], fontSize=8, leading=11, textColor=GREY, spaceAfter=4))
styles.add(ParagraphStyle(name='CodeX', parent=styles['Code'], fontName='Courier', fontSize=7.7, leading=11, textColor=INK, backColor=PALE, borderPadding=8, spaceBefore=4, spaceAfter=8))
styles.add(ParagraphStyle(name='Callout', parent=styles['BodyText'], fontSize=9.2, leading=14, textColor=NAVY, backColor=PALE, borderPadding=9, spaceBefore=6, spaceAfter=8))

class Architecture(Flowable):
    def __init__(self, width=168*mm, height=48*mm):
        super().__init__(); self.width=width; self.height=height
    def draw(self):
        c=self.canv
        boxes=[(0,24,48,24,'Institution','Authorized issuer'),(60,24,48,24,'CertiChain','Solidity contract'),(120,24,48,24,'Verifier','Public read access')]
        for x,y,w,h,title,sub in boxes:
            c.setFillColor(PALE if title!='CertiChain' else NAVY); c.setStrokeColor(BLUE); c.roundRect(x*mm,y*mm,w*mm,h*mm,3*mm,fill=1,stroke=1)
            c.setFillColor(colors.white if title=='CertiChain' else NAVY); c.setFont('Helvetica-Bold',9); c.drawCentredString((x+w/2)*mm,(y+14)*mm,title)
            c.setFillColor(colors.white if title=='CertiChain' else GREY); c.setFont('Helvetica',7); c.drawCentredString((x+w/2)*mm,(y+7)*mm,sub)
        c.setStrokeColor(TEAL); c.setLineWidth(1.5)
        c.line(48*mm,36*mm,60*mm,36*mm); c.line(108*mm,36*mm,120*mm,36*mm)
        c.line(57*mm,37.5*mm,60*mm,36*mm); c.line(57*mm,34.5*mm,60*mm,36*mm)
        c.line(117*mm,37.5*mm,120*mm,36*mm); c.line(117*mm,34.5*mm,120*mm,36*mm)
        c.setFillColor(GREY); c.setFont('Helvetica',7)
        c.drawCentredString(54*mm,42*mm,'issue / revoke')
        c.drawCentredString(114*mm,42*mm,'verify hash')
        c.setFillColor(BLUE); c.setFont('Helvetica-Bold',8)
        c.drawCentredString(84*mm,10*mm,'Only digest + issuer + status are recorded on-chain')
        c.setStrokeColor(TEAL); c.line(84*mm,24*mm,84*mm,16*mm)

def footer(canvas, doc):
    canvas.saveState(); w,h=A4
    if doc.page>1:
        canvas.setStrokeColor(colors.HexColor('#D7E2E8')); canvas.line(20*mm,15*mm,w-20*mm,15*mm)
        canvas.setFont('Helvetica',8); canvas.setFillColor(GREY)
        canvas.drawString(20*mm,10*mm,'CERTICHAIN  |  DIGITAL CREDENTIAL INFRASTRUCTURE')
        canvas.drawRightString(w-20*mm,10*mm,f'{doc.page}')
    canvas.restoreState()

def P(text, style='Bodyx'): return Paragraph(text, styles[style])
def bullet(text): return P('&bull;&nbsp; '+text)

doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=20*mm,leftMargin=20*mm,topMargin=10*mm,bottomMargin=22*mm,title='CertiChain - On-chain Credential Registry',author='Engineering Portfolio Prototype')
story=[]
# cover
story += [Spacer(1,27*mm),P('DIGITAL CREDENTIAL INFRASTRUCTURE','CoverSub'),P('CertiChain','CoverTitle'),P('Privacy-aware on-chain credential verification','CoverSub'),Spacer(1,5*mm)]
cover=Table([[P('<b>Project type</b><br/>Decentralized verification registry','Bodyx'),P('<b>Platform</b><br/>Ethereum-compatible EVM','Bodyx')],[P('<b>Implementation</b><br/>Solidity 0.8.x','Bodyx'),P('<b>Demo environment</b><br/>Remix VM / local Ganache','Bodyx')]],colWidths=[78*mm,78*mm],rowHeights=[22*mm,22*mm])
cover.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('BOX',(0,0),(-1,-1),0.6,colors.HexColor('#C8DCE3')),('INNERGRID',(0,0),(-1,-1),0.5,colors.white),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),8)]))
story += [cover,Spacer(1,10*mm),P('A minimal decentralized registry that lets an institution publish a certificate fingerprint and lets any verifier check its issuance and current revocation status. Personal information and certificate files remain off-chain.','Callout'),Spacer(1,20*mm),P('Engineering portfolio prototype','Smallx'),P('Date: October 2026','Smallx'),PageBreak()]
# report
story += [P('1. Project Overview','H1x'),P('Academic certificates are commonly verified by contacting the issuing institution or consulting a central database. That process can be slow, difficult across institutions, and vulnerable to a single database being altered or unavailable. CertiChain demonstrates how an Ethereum smart contract can provide a shared, append-only record of certificate fingerprints and issuer actions.','Bodyx'),P('The contract does not publish a certificate or personal details. The issuer hashes a canonical digital file off-chain and writes only the 32-byte digest, issuer wallet, timestamp, and revocation state. A verifier hashes the supplied file and queries the contract. A matching digest indicates that this exact file fingerprint was registered; it does not independently prove the academic claims in the document.','Bodyx'),P('2. Product Context','H1x'),P('Institutions and employers need a quick way to detect altered certificate files and confirm whether a record was issued and later revoked. A single institution-controlled database creates a central point of failure and makes cross-organization verification dependent on manual coordination. The project explores a shared ledger while keeping sensitive document content off-chain.','Bodyx'),P('3. Design Goals','H1x'),bullet('Build an issuer-gated Solidity registry for certificate fingerprints.'),bullet('Allow authorized issuers to register a fingerprint once and emit an auditable event.'),bullet('Allow the issuing institution or registry owner to revoke a record.'),bullet('Expose a public read function returning existence, validity, issuer, and issue time.'),bullet('Demonstrate transaction state changes in an EVM-compatible local environment.'),P('4. Technical Stack','H1x'),P('<b>Solidity:</b> contract language, compiler target 0.8.x. <b>Ethereum Virtual Machine:</b> execution and persistent state model. <b>Remix IDE:</b> compile, deploy to Remix VM, and call contract methods. <b>Ganache:</b> optional local JSON-RPC development chain. <b>Browser UI:</b> responsive wallet-connected interface using ethers.js for contract calls and browser-native SHA-256 file hashing. The interface supports verification, issuance, and revocation; no public deployment is claimed.','Bodyx'),P('5. System Architecture','H1x'),Architecture(),P('Data flow: issuer canonicalizes the document, computes its digest, then submits a transaction. EVM nodes execute the contract and replicate the resulting state under the selected network consensus. A verifier independently computes the digest and makes a read-only query. A read call does not change chain state; issuance and revocation require signed transactions and gas.','Bodyx'),PageBreak()]
story += [P('6. Smart Contract Design','H1x'),P('The source file is <b>contracts/CertiChain.sol</b>. Registry storage maps each bytes32 digest to issuer address, issue timestamp, revoked flag, and existence flag. A separate mapping controls authorized issuer wallets. The deployer is the owner and is authorized by the constructor.','Bodyx')]
rows=[[P('<b>Function / event</b>','Smallx'),P('<b>Purpose and access</b>','Smallx')],
[P('setIssuerAuthorization(address,bool)','Code'),P('Owner-only. Grants or removes issuer permission; rejects the zero address.','Bodyx')],
[P('issueCertificate(bytes32)','Code'),P('Authorized issuers only. Rejects empty and duplicate hashes; records issuer and timestamp; emits CertificateIssued.','Bodyx')],
[P('revokeCertificate(bytes32)','Code'),P('Only original issuer or owner. Marks an existing record revoked once; emits CertificateRevoked.','Bodyx')],
[P('verifyCertificate(bytes32)','Code'),P('Public view. Returns existence, current validity, issuer, and issue time.','Bodyx')],
[P('IssuerAuthorizationChanged','Code'),P('Audit event when issuer permission changes.','Bodyx')]]
t=Table(rows,colWidths=[67*mm,91*mm],repeatRows=1)
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#CAD8DE')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
story += [t,Spacer(1,8),P('Access control and trust assumptions','H2x'),P('Authorization prevents arbitrary wallets from issuing records, but the owner remains a governance authority. If the owner key is compromised, an attacker could authorize a malicious issuer. Revocation is intentionally visible and does not erase history. The contract cannot determine whether a file is academically legitimate; it only manages the digest-to-issuer assertion made by an authorized account.','Bodyx'),P('<b>Consensus:</b> Ethereum mainnet uses proof-of-stake validators to agree on canonical blocks and state. Remix VM and Ganache are local development environments; they do not demonstrate mainnet validator consensus.','Bodyx'),P('7. Demonstration Output','H1x'),P('The following is an expected Remix VM interaction transcript to reproduce. It is clearly illustrative and is not presented as a transaction captured from a deployed chain. Capture your own Remix screenshots after running the README steps if the submission requires screenshots.','Callout'),P('Deploy CertiChain from account[0]          success; account[0] is owner and issuer<br/>Issue 0x7f...a91c from account[0]          success; CertificateIssued event<br/>Verify 0x7f...a91c                         exists=true, valid=true, issuer=account[0]<br/>Revoke 0x7f...a91c from account[0]        success; CertificateRevoked event<br/>Verify 0x7f...a91c again                   exists=true, valid=false<br/>Issue from unauthorized account            reverted: caller is not authorized','Code'),P('Expected transaction behavior','H2x'),P('Issuance and revocation are state-changing transactions. Each consumes gas and emits an event. Verification is a view call and can be executed without a transaction fee in Remix. Remix VM resets on environment reset; Ganache can be used when repeatable local chain state is preferred.','Bodyx'),PageBreak()]
story += [P('8. Run the Prototype','H1x'),P('1. Open Remix IDE and create a Solidity file from contracts/CertiChain.sol.<br/>2. Select compiler 0.8.24 or a compatible Solidity 0.8.x release and compile.<br/>3. Choose Remix VM in Deploy &amp; Run, select account[0], and deploy.<br/>4. Use an off-chain SHA-256 digest of a sample file as bytes32 input to issueCertificate.<br/>5. Query verifyCertificate from any account, revoke as issuer/owner, and query again.<br/>6. To use Ganache, start a local chain and connect Remix to its RPC provider; record chain ID, address, and transaction hashes in the README after deployment.','Bodyx'),P('The included helper scripts/hash_certificate.py prints a 32-byte SHA-256 fingerprint in 0x-prefixed form. Use a sample or synthetic document only. A production system must specify canonicalization because file metadata or encoding changes can alter the digest.','Bodyx'),P('9. Product Assessment','H1x'),P('CertiChain demonstrates a practical blockchain pattern: use a smart contract as a shared registry of issuer claims, preserve a transparent event trail, restrict writes to authorized wallets, and allow public verification. The demonstration highlights replicated state and transaction execution on an EVM chain while keeping document data outside the ledger.','Bodyx'),P('The design has clear limits. A digest match proves file identity relative to a prior registration, not the truth of the certificate. Access to the source file is still necessary to compute a matching digest. Public chains create permanent metadata, and the registry owner introduces a governance trust assumption.','Bodyx'),P('10. Roadmap','H1x'),bullet('Add a multisignature issuer-administration policy and issuer key rotation.'),bullet('Add issuer administration and network-aware controls to the browser interface.'),bullet('Support revocation reasons through privacy-safe controlled codes or a signed off-chain statement.'),bullet('Add independent contract review, automated security analysis, and deployment verification.'),bullet('Evaluate a permissioned consortium chain if institutions need controlled validator membership.'),P('References and project files','H1x'),P('Solidity documentation: https://docs.soliditylang.org/<br/>Hardhat documentation: https://hardhat.org/docs/getting-started<br/>Remix IDE: https://remix.ethereum.org/<br/>Project source and run instructions: README.md and contracts/CertiChain.sol','Smallx'),P('Portfolio status: the interface and contract are prepared for local EVM demonstration. No public deployment, audited security review, or production use is claimed.','Callout')]
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)








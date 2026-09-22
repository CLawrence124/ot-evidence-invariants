"""Two local stdio tools, backed by ordinary independently tested Python."""
from mcp.server.fastmcp import FastMCP

from ot_dossier.domain.evidence_assembler import assemble_target_disease_evidence as assemble
from ot_dossier.domain.dossier_validator import validate_dossier_references as validate
from ot_dossier.domain.models import Dossier, EvidencePacket, ValidationResult

mcp = FastMCP("Open Targets Evidence Invariants")
_packets: dict[str, EvidencePacket] = {}


@mcp.tool()
def assemble_target_disease_evidence(target: str, disease: str = "IBD") -> EvidencePacket:
    """Replay frozen evidence for NOD2/TNF and IBD. Returns scoped records and typed missingness."""
    packet = assemble(target, disease)
    _packets[packet.packet_id] = packet
    return packet


@mcp.tool()
def validate_dossier_references(packet_id: str, dossier: Dossier) -> ValidationResult:
    """Check references and structured assertions against a previously assembled packet. Not entailment."""
    if packet_id not in _packets:
        raise ValueError("Unknown packet_id: assemble the packet in this server process first")
    return validate(_packets[packet_id], dossier)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

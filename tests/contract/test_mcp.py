import asyncio
import os
from pathlib import Path
import sys

import jsonschema
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ot_dossier.cli import review_dossier
from ot_dossier.domain.models import EvidencePacket


def test_two_tools_over_real_stdio():
    async def scenario():
        root = Path(__file__).resolve().parents[2]
        params = StdioServerParameters(command=sys.executable, args=["-m", "ot_dossier.mcp.server"],
            env={**os.environ, "PYTHONPATH": str(root / "src")}, cwd=str(root))
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                listing = await session.list_tools()
                schemas = {t.name:t.outputSchema for t in listing.tools}
                assert set(schemas) == {"assemble_target_disease_evidence", "validate_dossier_references"}
                result = await session.call_tool("assemble_target_disease_evidence", {"target":"NOD2", "disease":"IBD"})
                assert not result.isError
                jsonschema.validate(result.structuredContent, schemas["assemble_target_disease_evidence"])
                packet = EvidencePacket.model_validate(result.structuredContent)
                dossier = review_dossier(packet)
                result = await session.call_tool("validate_dossier_references", {"packet_id":packet.packet_id,"dossier":dossier.model_dump(mode="json")})
                assert not result.isError
                jsonschema.validate(result.structuredContent, schemas["validate_dossier_references"])
                assert result.structuredContent["valid"]
                bad = await session.call_tool("assemble_target_disease_evidence", {"target":"BAD"})
                assert bad.isError
                unknown = await session.call_tool("validate_dossier_references", {"packet_id":"unknown","dossier":dossier.model_dump(mode="json")})
                assert unknown.isError
                d = dossier.model_dump(mode="json")
                d["claims"][0]["record_refs"] = ["rec_nonexistent"]
                bad_dossier = await session.call_tool("validate_dossier_references", {"packet_id":packet.packet_id,"dossier":d})
                assert not bad_dossier.isError  # Valid request; validation findings are structured domain results.
                assert not bad_dossier.structuredContent["valid"]
    asyncio.run(scenario())

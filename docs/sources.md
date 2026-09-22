# Primary sources checked during implementation

- [Open Targets GraphQL documentation](https://platform-docs.opentargets.org/data-access/graphql-api):
  endpoint and POST request format. Actual queries were executed; raw responses
  and exact selections are in `fixtures/cassettes/26.06`.
- [Open Targets associations](https://platform-docs.opentargets.org/associations):
  direct/descendant selection and score interpretation. Documentation's historic
  NOD2/IBD example remains useful conceptually; live entity identifiers differ.
- [Official Open Targets MCP](https://platform-docs.opentargets.org/data-access/model-context-protocol):
  existing upstream server; our project does not assert comparative performance.
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) and
  [v1 documentation](https://py.sdk.modelcontextprotocol.io/v1/): the currently
  installed and tested SDK is 1.30.0 with built-in FastMCP. Main now documents v2.
  Verified structured results through a real stdio client, not just decorator syntax.
- [Open Targets licence](https://platform-docs.opentargets.org/licence) and
  [citation](https://platform-docs.opentargets.org/citation): public data attribution.

Live entity query returned data release 26.06 and API 26.6.3. Capture UTC timestamps
are authoritative for retrieval time; release metadata is not a capture timestamp.
Installed dependency versions are in `requirements.lock`. No current Sonnet model
or Anthropic SDK version is claimed verified in this phase because no model loop
has been implemented.

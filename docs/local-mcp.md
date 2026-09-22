# Local MCP walkthrough (VS Code on macOS)

A **checkout** means this local project folder. Its **virtual environment** is the
`.venv` folder holding the Python interpreter and packages used for this project.
The **server** is a running Python program offering our two tools. **Stdio** means
it receives machine-readable messages on standard input and sends responses on
standard output. There is no browser page, URL, or network port to open.
See the [MCP architecture guide](https://modelcontextprotocol.io/docs/learn/architecture)
for the distinction between a host, client, server, and transport.

There are two useful exercises below: starting the server yourself, then letting
our test client start it and actually call its tools. Starting the server alone
neither connects an AI model nor creates a dossier.

### 1. Open a terminal in the project folder

In VS Code, open the `ot-evidence-invariants` folder with **File → Open Folder**,
then choose **Terminal → New Terminal**. Type each command into that terminal and
press Return; do not paste the commands into a Python file or a Python `>>>` prompt.
If you see `>>>`, type `exit()` first to return to the shell.

```bash
pwd
ls
```

`pwd` prints your current directory. `ls` lists its files. You should see
`README.md`, `pyproject.toml`, `requirements.lock`, `src`, and `tests`.
If you are elsewhere, run `cd` followed by the path to this project folder.
For example, if you cloned into a Projects directory:

```bash
cd ~/Projects/ot-evidence-invariants
```

Substitute your actual clone location. All commands below run from that directory.

### 2. Activate the project's Python environment

If you already created `.venv` through VS Code or the setup instructions, reuse it:

```bash
source .venv/bin/activate
python -c "import sys; print(sys.executable)"
python --version
```

The executable path should end with `ot-evidence-invariants/.venv/bin/python`.
For this walkthrough, use Python 3.12. Activation makes this terminal find the
project's Python and commands first; it does not change Python for your entire
computer. You may see `(.venv)` in the prompt, but the executable path is the
more reliable check. Reactivate in each new terminal unless VS Code does it for you.

If activation reports **No such file or directory**, the `.venv` folder is absent
or you are in the wrong directory. After checking Step 1, create it once:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

If `python3.12` is not found, run `python3 --version`. If that reports 3.12.x, use
`python3 -m venv .venv` instead. Otherwise select or install Python 3.12 before
continuing. Do not recreate an existing working environment merely to activate it.
In VS Code, also use **Python: Select Interpreter** and select this `.venv` so
editor features and terminal commands use the same environment.

### 3. Install dependencies and register the project's commands

With the environment active, run these in order. If you already completed the
same installation successfully in this `.venv`, skip to Step 4.

```bash
python -m pip install -r requirements.lock
python -m pip install --no-deps --no-build-isolation -e .
```

The first command installs the pinned packages we tested. The second installs
this project in **editable mode**: changes to its source files take effect without
reinstalling it. The final `.` means “the current folder.” The extra flags reuse
the dependencies/build tools installed by the first command.

Installation creates `ot-dossier` and `ot-dossier-mcp` commands inside `.venv/bin`.
Check the server command's location:

```bash
command -v ot-dossier-mcp
```

It should end with `ot-evidence-invariants/.venv/bin/ot-dossier-mcp`. If it is
missing or points elsewhere, recheck activation and the editable installation.
Do not install packages globally to fix that problem.

### 4. Start the server manually and observe it waiting

```bash
ot-dossier-mcp
```

**Expected behavior:** the terminal stays occupied, usually with little or no
output. If no error appears and the prompt does not return, the process is waiting
for an MCP client. This is expected, but does not yet prove the tools work.
Do not type ordinary questions or shell commands into this waiting server.
Its input expects protocol messages, not a chat conversation.

Press **Control+C** to stop it and return to the shell prompt. An interrupt or
cancellation message on shutdown can be normal. The explicit-path equivalent is
`.venv/bin/ot-dossier-mcp`; this chooses the environment's command without relying
on activation. It still assumes you are in the project directory.

### 5. Verify that a real MCP client can use both tools

After stopping the manually started server, run:

```bash
python -m pytest tests/contract/test_mcp.py -v
```

Expected outcome: `test_two_tools_over_real_stdio PASSED` and `1 passed`.
The test launches **its own** server process and closes it afterward. It does not
attach to the manual server from Step 4, so you do not need a second terminal or
a background server. The test uses the same server module through the current
Python interpreter.

During this test, the client:

1. Establishes an MCP session with the server.
2. Requests the tool list and confirms our two tools exist.
3. Calls `assemble_target_disease_evidence` for NOD2–IBD.
4. Builds a deterministic test dossier and calls `validate_dossier_references`.
5. Checks that output structures match their declared JSON schemas.
6. Sends deliberate bad inputs, including a nonexistent citation, and confirms
   that the expected errors/findings appear.

A **contract test** checks whether two components communicate using the agreed
input/output format and behavior. Here it checks the actual MCP connection,
not just whether a Python function works. A passing result does not mean a model
wrote the dossier or that a scientist verified its claims. The test requires no
model key, account, or API payment; source evidence comes from frozen local files.

### 6. Generate a dossier you can read

To write files rather than start a waiting MCP server, run:

```bash
ot-dossier --target NOD2 --disease IBD --out generated
```

Open `generated/nod2_ibd.md` in VS Code. The same directory also contains packet,
dossier, and validation JSON. These remain deterministic review drafts.
`ot-dossier` calls the domain services directly; it does not need the MCP server
running. The contract test in Step 5 is what verifies the MCP route.

When you run the simulated agent, its client launches the local server automatically,
sends tool calls, and receives results. You will not need to manually leave a server
running in another terminal. Connecting this server to a particular AI host is a
separate setup step and has not been done by the commands above.

### Common problems

| What you see | What it means / what to do |
|---|---|
| `ot-dossier-mcp: command not found` | Activate `.venv` and finish the editable install in Step 3. |
| `No module named pytest` or `mcp` | Check `sys.executable`, then install `requirements.lock` with that environment's Python. |
| `.venv/bin/activate: No such file or directory` | Check the current folder, then create `.venv` only if absent. |
| Server appears to do nothing | It may be correctly waiting for protocol input; stop it with Control+C and run Step 5. |
| Protocol/JSON errors after typing into the server | Stop it; ordinary text is not an MCP request. Use the test client. |
| Deliberate bad-identifier messages during testing | The test intentionally exercises errors. Check the final PASSED/FAILED result. |

The two tool contracts are:

- `assemble_target_disease_evidence(target, disease="IBD")` returns an EvidencePacket.
- `validate_dossier_references(packet_id, dossier)` checks against a packet already
  assembled in the same server process. Unknown handles are tool errors; invalid
  dossiers return structured findings with `valid: false`.


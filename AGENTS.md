# Repository Guidelines

## Project Overview

**dir-agent-profile** is a standalone Python CLI tool that manages named model role profiles for [oh-my-pi (OMP)](https://github.com/nicholasgasior/oh-my-pi). A profile defines a complete set of model role assignments (`default`, `plan`, `smol`, `slow`, `commit`). Profiles are persisted to a user-level YAML config and can be applied to any project by writing the `modelRoles` block into that project's `.omp/config.yml`.

The authoritative specification is `SYSTEM_SPEC.md` at the project root. All behavioral questions should be resolved against that document.

## Architecture & Data Flow

The tool operates on two YAML files:

```
User config (read/write)                       Project config (write target)
~/.config/omp-profiles.yml                     ./.omp/config.yml
┌──────────────────────────┐                   ┌──────────────────────────┐
│ profiles:                │                   │ modelRoles:              │
│   economy:               │  --apply NAME     │   default: ...           │
│     default: ...         │ ───────────────►  │   plan: ...              │
│     plan: ...            │                   │   smol: ...              │
│     ...                  │                   │   slow: ...              │
│   quality:               │                   │   commit: ...            │
│     ...                  │                   │ # other keys preserved   │
└──────────────────────────┘                   └──────────────────────────┘
```

Model discovery happens at runtime via `omp list-models` (subprocess call, stdout parsed).

### CLI Modes

| Invocation | Behavior |
|---|---|
| `dir-agent-profile` (no flags) | Interactive mode: main menu → select/create profile → apply |
| `--apply <name>` | Non-interactive: write named profile to `.omp/config.yml` |
| `--list` | Print all saved profiles and their role assignments |
| `--remove <name>` | Delete a named profile from user config |

### Interactive Flow (no flags)

1. **Main menu** — list saved profiles + "Create new profile" + "Quit". Selecting a profile applies it after confirmation.
2. **Role assignment** (create only) — for each of the five roles in order, present a searchable/fuzzy model selector. Support backward navigation (`← Back`) and display a running summary of assignments chosen so far.
3. **Confirm and name** — summary table, then prompt for profile name (validated: non-empty, `[a-zA-Z0-9_-]+`, overwrite confirmation if exists). Save to user config and apply to project.

## Key Directories

This is a single-script or small-package project. Expected layout:

```
omp-dir-agent-profiles/
├── AGENTS.md                  # This file — repository guidelines
├── SYSTEM_SPEC.md             # Authoritative behavioral specification
├── README.md                  # User-facing documentation
├── .gitignore
├── dir_agent_profile/         # Package root (or single script — see below)
│   ├── __init__.py
│   ├── __main__.py            # Entry point: argument parsing, mode dispatch
│   ├── cli.py                 # Interactive flow (questionary prompts)
│   ├── config.py              # Profile YAML read/write, XDG path resolution
│   ├── models.py              # `omp list-models` subprocess + parsing
│   └── apply.py               # Write modelRoles to .omp/config.yml
├── tests/
│   └── ...
└── pyproject.toml             # Project metadata, dependencies, script entry point
```

If the project is implemented as a single script instead, that script should live at the root (e.g. `dir_agent_profile.py`).

## Important Files

| File | Purpose |
|---|---|
| `SYSTEM_SPEC.md` | Authoritative specification — all behavior questions resolve here |
| `pyproject.toml` | Dependencies, script entry point, metadata |
| Config: `~/.config/omp-profiles.yml` | User-level profile storage (XDG-compliant) |
| Config: `.omp/config.yml` | Per-project OMP config — write target for `modelRoles` |

## Runtime & Tooling

- **Language:** Python 3.x (no minimum version specified; target 3.10+ for `match`/union syntax)
- **Dependencies:**
  - `PyYAML` or `ruamel.yaml` (prefer `ruamel.yaml` if comment preservation in `.omp/config.yml` is needed)
  - `questionary` for interactive prompts (fuzzy select, text input, confirm)
- **No build step.** Should run directly after `pip install` or from source.
- **External dependency:** `omp` CLI must be on `PATH` for model discovery (`omp list-models`)

### Config File Paths

Profile storage follows XDG:
1. `$XDG_CONFIG_HOME/omp-profiles.yml` (typically `~/.config/omp-profiles.yml`)
2. Fallback: `~/.omp-profiles.yml` if `XDG_CONFIG_HOME` is not set

## Code Conventions & Common Patterns

### YAML Handling

When writing to `.omp/config.yml`:
- **File does not exist** → create it with only the `modelRoles` block
- **File exists, has `modelRoles`** → replace only that key's contents; preserve all other settings
- **File exists, no `modelRoles`** → add the key

The five role keys written under `modelRoles` are exactly: `default`, `plan`, `smol`, `slow`, `commit`.

Use `ruamel.yaml` round-trip mode if preserving comments and formatting in existing config files is important. Otherwise `PyYAML` (`yaml.safe_load` / `yaml.dump`) suffices.

### Profile Name Validation

- Non-empty
- Characters: `[a-zA-Z0-9_-]` only (no spaces)
- If name already exists: prompt user to confirm overwrite

### Model Discovery

Run `omp list-models` as a subprocess, parse stdout. Sort results:
1. Group by provider
2. Alphabetical by model name within each provider group

### Error Handling

| Condition | Behavior |
|---|---|
| `omp` not on `PATH` | Exit with clear message; do not proceed |
| `omp list-models` fails or empty output | Exit with message; do not proceed to role assignment |
| `.omp/` directory missing in cwd | Create it |
| `~/.config/omp-profiles.yml` missing | Treat as empty profile list; create on first save |

General principle: fail early with clear messages. Do not swallow errors or present partial UI when a prerequisite is missing.

### CLI Argument Parsing

Use `argparse` (stdlib). Flags are mutually exclusive: `--apply`, `--list`, `--remove`, or no flags (interactive mode).

### Interactive UI

`questionary` library patterns:
- `questionary.select()` for main menu and model selection (with fuzzy filtering)
- `questionary.text()` for profile name input (with validation callback)
- `questionary.confirm()` for overwrite and apply confirmations

## Testing & QA

### Test Strategy

- **Unit tests** for config read/write, profile validation, YAML merge logic, model list parsing
- **Integration tests** for CLI flag dispatch (mock subprocess calls to `omp list-models`)
- **Do not mock** the YAML library itself — test against real YAML round-trips
- Interactive flows are difficult to unit-test; focus on testing the logic functions they call

### Key Test Scenarios

1. Apply profile to nonexistent `.omp/config.yml` → file created with only `modelRoles`
2. Apply profile to existing config with other keys → only `modelRoles` replaced, other keys intact
3. Apply profile to existing config without `modelRoles` → key added
4. Profile name validation rejects spaces, empty strings, special characters
5. `--remove` on nonexistent profile → graceful error
6. `--apply` on nonexistent profile → graceful error
7. `omp list-models` returns empty → early exit with message

### Running Tests

```bash
# Once test infrastructure exists:
python -m pytest tests/ -v

# Single file:
python -m pytest tests/test_config.py -v
```

## Development Commands

```bash
# Install dependencies
pip install pyyaml questionary
# or with ruamel.yaml:
pip install ruamel.yaml questionary

# Run the tool (from repo root)
python -m dir_agent_profile
# or if installed as a script:
dir-agent-profile

# Run tests
python -m pytest tests/ -v

# Type checking (optional, if type hints are used)
mypy dir_agent_profile/
```

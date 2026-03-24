# `dir-agent-profile` — Directory Agent Profile Manager

## Purpose

A standalone CLI script that manages named model role profiles for oh-my-pi. Profiles define a complete set of model role assignments (`default`, `plan`, `smol`, `slow`, `commit`) and are persisted to a user-level config file. Applying a profile writes the role assignments to `.omp/config.yml` in the current working directory, which takes precedence over the user-global OMP config for that project.

---

## Runtime

Python 3.x. Dependencies: `PyYAML` (or `ruamel.yaml` if comment preservation is needed), `questionary` (interactive prompts). Should run without installation beyond `pip install`.

---

## User Config File

Profiles are stored at `~/.config/omp-profiles.yml` (XDG-compliant; fall back to `~/.omp-profiles.yml` if `XDG_CONFIG_HOME` is not set). Format:

```yaml
profiles:
    economy:
        default: gemini-2.5-flash
        plan: gemini-2.5-flash
        smol: gemini-2.5-flash
        slow: gemini-2.5-pro:high
        commit: gemini-2.5-flash
    quality:
        default: anthropic/claude-sonnet-4-20250514
        plan: anthropic/claude-opus-4-1:high
        smol: anthropic/claude-haiku-4-5
        slow: anthropic/claude-opus-4-1:high
        commit: anthropic/claude-sonnet-4-20250514
```

---

## Invocation

```
dir-agent-profile [--apply <profile-name>] [--list] [--remove <profile-name>]
```

| Flag              | Behaviour                                                    |
| ----------------- | ------------------------------------------------------------ |
| _(no flags)_      | Launch interactive mode                                      |
| `--apply <name>`  | Directly write the named profile to `.omp/config.yml`, no UI |
| `--list`          | Print all saved profiles and their role assignments          |
| `--remove <name>` | Delete a named profile from the user config file             |

---

## Interactive Flow

### Step 1 — Main menu

Present a selection list containing:

- One entry per saved profile (selecting one applies it immediately after a confirmation prompt)
- "Create new profile"
- "Quit"

### Step 2 — Role assignment (new profile only)

Retrieve available models by running `omp list-models` and parsing stdout. Sort results grouped by provider, then alphabetically by model name within each provider group.

For each of the five roles in order (`default`, `plan`, `smol`, `slow`, `commit`):

- Present a searchable/fuzzy list of all available models
- Allow backward navigation between roles (e.g. selecting "← Back" re-presents the previous role's selector with the current selection pre-highlighted)
- Display a running summary of current assignments at the top of each role prompt so the user can see what they have chosen so far

### Step 3 — Confirm and name

Display a summary table of the complete role → model assignment. Prompt for a profile name with the following validation rules:

- Non-empty
- No spaces; alphanumeric characters plus hyphens and underscores only
- If the name already exists, prompt the user to confirm overwrite before proceeding

On confirmation: save to `~/.config/omp-profiles.yml` and apply to `./.omp/config.yml`.

---

## Applying a Profile

When writing to `.omp/config.yml`:

- If the file does not exist, create it containing only the `modelRoles` block
- If the file exists and already has a `modelRoles` key, replace only that key's contents, preserving all other settings intact
- If the file exists but has no `modelRoles` key, add it

The five roles written are exactly `default`, `plan`, `smol`, `slow`, `commit` as sub-keys of `modelRoles`.

---

## Error Handling

| Condition                                    | Behaviour                                            |
| -------------------------------------------- | ---------------------------------------------------- |
| `omp` not found on `PATH`                    | Exit with a clear message; do not proceed            |
| `omp list-models` fails or returns no output | Exit with message; do not proceed to role assignment |
| `.omp/` directory does not exist in cwd      | Create it                                            |
| `~/.config/omp-profiles.yml` does not exist  | Treat as empty profile list; create on first save    |

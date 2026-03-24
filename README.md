# dir-agent-profile

Directory-level model role profile manager for [Oh My Pi](https://github.com/nicepkg/omp). Manage named sets of model role assignments (`default`, `plan`, `smol`, `slow`, `commit`) and apply them per-project via `.omp/config.yml`.

## Requirements

- Python 3.9+
- `omp` installed and on `PATH` (needed to discover available models)

## Installation

```bash
pip install .
```

This installs the `dir-agent-profile` command and its dependencies (`PyYAML`, `questionary`).

If pip warns that the script directory is not on `PATH`, either add it or invoke via:

```bash
python -m dir_agent_profile
```

## Usage

### Interactive mode (default)

```bash
dir-agent-profile
```

Launches a TUI that lets you:

1. **Apply** a saved profile to the current directory
2. **Create** a new profile by selecting a model for each role from a searchable list

### Non-interactive flags

```
dir-agent-profile --list              # Print all saved profiles
dir-agent-profile --apply <name>      # Apply a profile to .omp/config.yml
dir-agent-profile --remove <name>     # Delete a saved profile
```

## How it works

Profiles are stored at `~/.config/omp-profiles.yml` (respects `$XDG_CONFIG_HOME`). Applying a profile writes the `modelRoles` block to `.omp/config.yml` in the current working directory, which OMP reads as a project-level override. Other keys in an existing `config.yml` are preserved.

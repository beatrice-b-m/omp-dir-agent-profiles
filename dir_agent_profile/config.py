from __future__ import annotations

from pathlib import Path

import yaml


def apply_profile(roles: dict[str, str], target_dir: Path | None = None) -> None:
    """Write modelRoles to .omp/config.yml in target_dir (defaults to cwd).

    Preserves all other top-level keys in an existing config.yml.
    Creates .omp/ directory if needed.
    """
    base = target_dir or Path.cwd()
    omp_dir = base / ".omp"
    omp_dir.mkdir(parents=True, exist_ok=True)

    config_path = omp_dir / "config.yml"
    if config_path.exists():
        data = yaml.safe_load(config_path.read_text())
        config: dict = data if isinstance(data, dict) else {}
    else:
        config = {}

    config["modelRoles"] = dict(roles)
    config_path.write_text(yaml.dump(config, default_flow_style=False, sort_keys=False))

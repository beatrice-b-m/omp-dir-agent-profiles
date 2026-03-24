from __future__ import annotations

import os
from pathlib import Path

import yaml


def get_profiles_path() -> Path:
    """XDG-compliant path: $XDG_CONFIG_HOME/omp-profiles.yml or ~/.config/omp-profiles.yml"""
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "omp-profiles.yml"
    return Path.home() / ".config" / "omp-profiles.yml"


def load_profiles() -> dict[str, dict[str, str]]:
    """Load all profiles. Returns {} if file missing, empty, or malformed."""
    path = get_profiles_path()
    try:
        data = yaml.safe_load(path.read_text())
    except FileNotFoundError:
        return {}
    if not isinstance(data, dict):
        return {}
    profiles = data.get("profiles", {})
    if not isinstance(profiles, dict):
        return {}
    return profiles


def save_profiles(profiles: dict[str, dict[str, str]]) -> None:
    """Write all profiles to disk. Creates parent dirs."""
    path = get_profiles_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump({"profiles": profiles}, default_flow_style=False, sort_keys=False))


def get_profile(name: str) -> dict[str, str] | None:
    """Get one profile by name."""
    return load_profiles().get(name)


def save_profile(name: str, roles: dict[str, str]) -> None:
    """Save or overwrite a single profile."""
    profiles = load_profiles()
    profiles[name] = roles
    save_profiles(profiles)


def remove_profile(name: str) -> bool:
    """Delete a profile. Returns True if it existed."""
    profiles = load_profiles()
    if name not in profiles:
        return False
    del profiles[name]
    save_profiles(profiles)
    return True

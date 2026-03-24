from __future__ import annotations

import re
from itertools import groupby

import questionary

from dir_agent_profile import ROLES
from dir_agent_profile.config import apply_profile
from dir_agent_profile.models import fetch_models
from dir_agent_profile.profiles import load_profiles, save_profile


def run_interactive() -> None:
    """Full interactive flow: main menu -> apply existing / create new -> save + apply."""
    profiles = load_profiles()

    choices: list = []
    for name in profiles:
        choices.append(questionary.Choice(f"Apply: {name}", value=("apply", name)))
    choices.append(questionary.Choice("Create new profile", value=("create", None)))
    choices.append(questionary.Choice("Quit", value=("quit", None)))

    answer = questionary.select("Select an action:", choices=choices).ask()
    if answer is None or answer[0] == "quit":
        return

    action, name = answer
    if action == "apply":
        _apply_existing(name, profiles)
    elif action == "create":
        _create_new(profiles)


def _apply_existing(name: str, profiles: dict) -> None:
    """Print profile roles table, confirm, then apply."""
    _print_profile(name, profiles[name])
    confirmed = questionary.confirm(f"Apply profile '{name}'?").ask()
    if confirmed is None or not confirmed:
        print("Cancelled.")
        return
    apply_profile(profiles[name])
    print(f"Profile '{name}' applied.")


def _create_new(existing_profiles: dict) -> None:
    """Walk role assignment, confirm name, save and apply."""
    models = fetch_models()
    assignments = _assign_roles(models)
    if assignments is None:
        print("Cancelled.")
        return

    _print_profile("(new)", assignments)

    while True:
        name = questionary.text("Profile name:", validate=_validate_name).ask()
        if name is None:
            return
        if name in existing_profiles:
            overwrite = questionary.confirm(
                f"Profile '{name}' already exists. Overwrite?"
            ).ask()
            if overwrite is None or not overwrite:
                continue
        break

    save_profile(name, assignments)
    apply_profile(assignments)
    print(f"Profile '{name}' saved and applied.")


def _assign_roles(models: list[str]) -> dict[str, str] | None:
    """Walk through ROLES with back navigation. Returns assignments or None on cancel."""
    # Group models by provider once; fresh Choice objects are built each iteration
    # because questionary mutates them in-place (shortcut key assignment).
    grouped: list[tuple[str, list[str]]] = []
    for provider, group in groupby(models, key=lambda m: m.split("/", 1)[0]):
        grouped.append((provider, list(group)))

    def _build_model_choices() -> list:
        choices: list = []
        for provider, provider_models in grouped:
            choices.append(questionary.Separator(f"\u2500\u2500 {provider} \u2500\u2500"))
            for model_id in provider_models:
                choices.append(questionary.Choice(model_id, value=model_id))
        return choices

    i = 0
    assignments: dict[str, str] = {}

    while i < len(ROLES):
        role = ROLES[i]

        # Running summary: roles already assigned (indices strictly before i).
        if i > 0:
            print("\nAssigned so far:")
            for j in range(i):
                print(f"  {ROLES[j]}: {assignments[ROLES[j]]}")

        choices: list = []
        if i > 0:
            choices.append(questionary.Choice("\u2190 Back", value="__BACK__"))
        choices.extend(_build_model_choices())

        default = assignments.get(role)
        answer = questionary.select(
            f"Select model for '{role}':",
            choices=choices,
            default=default,
            use_search_filter=True,
            use_jk_keys=False,
            pointer="\u00bb",
            instruction="(type to search)",
        ).ask()

        if answer is None:
            return None
        if answer == "__BACK__":
            i -= 1
            continue

        assignments[role] = answer
        i += 1

    return assignments


def _validate_name(name: str) -> bool | str:
    """Validate profile name: non-empty alphanumeric with hyphens/underscores."""
    if re.fullmatch(r"[a-zA-Z0-9_-]+", name):
        return True
    return "Name must be non-empty, alphanumeric with hyphens/underscores only."


def _print_profile(name: str, roles: dict[str, str]) -> None:
    """Print a formatted profile table."""
    print(f"\nProfile: {name}")
    print(f"  {'Role':<10}  Model")
    print(f"  {'-'*10}  {'-'*40}")
    for role in ROLES:
        model = roles.get(role, "(unset)")
        print(f"  {role:<10}  {model}")
    print()

#!/usr/bin/env python3
"""
Logic Plugin Signer — macOS Audio Plugin Inspection & Ad-hoc Signing Tool
Inspects, removes Gatekeeper quarantine, and ad-hoc signs AU, VST3, CLAP, VST, and Standalone audio plugins.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

STANDARD_PLUGIN_DIRS = [
    Path("~/Library/Audio/Plug-Ins").expanduser(),
    Path("/Library/Audio/Plug-Ins"),
    Path("/Volumes/data1/AI_Gerelateerd/github/muziek_gerelateerd"),
    Path("/Applications"),
]

PLUGIN_EXTENSIONS = {".component", ".vst3", ".clap", ".vst", ".app"}


def find_plugin(target_query: str, ledger_path: Path | None = None) -> Path | None:
    """Find a plugin path by exact path, ledger cache, or targeted directory scan."""
    p = Path(target_query).expanduser()
    if p.exists():
        return p.resolve()

    clean_name = target_query.strip()
    variations = [clean_name]
    for ext in PLUGIN_EXTENSIONS:
        if not clean_name.lower().endswith(ext):
            variations.append(f"{clean_name}{ext}")
            # Strip suffix if joined, e.g. GridlineTestvst3 -> GridlineTest.vst3
            stripped = re.sub(rf"{ext.lstrip('.')}$", "", clean_name, flags=re.IGNORECASE)
            if stripped != clean_name:
                variations.append(f"{stripped}{ext}")
                variations.append(stripped)

    # 1. Check ledger cache (components.tsv)
    if ledger_path and ledger_path.exists():
        try:
            with open(ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split("\t")
                    if len(parts) >= 3:
                        name, _, path_str = parts[0], parts[1], parts[2]
                        for var in variations:
                            if var.lower() in [name.lower(), Path(path_str).name.lower(), Path(path_str).stem.lower()]:
                                candidate = Path(path_str)
                                if candidate.exists():
                                    return candidate.resolve()
        except Exception:
            pass

    # 2. Search in standard & audio dev locations (shallow / maxdepth 4 for speed)
    for base_dir in STANDARD_PLUGIN_DIRS:
        if not base_dir.exists():
            continue
        for var in variations:
            # Check direct or up to depth 4
            for ext in PLUGIN_EXTENSIONS:
                matches = list(base_dir.glob(f"**/{var}"))
                if matches:
                    return matches[0].resolve()

    # 3. Check mdfind quickly with timeout
    for var in variations:
        try:
            res = subprocess.run(
                ["mdfind", "-name", var],
                capture_output=True,
                text=True,
                timeout=2,
                stdin=subprocess.DEVNULL,
            )
            for line in res.stdout.strip().splitlines():
                found = Path(line.strip())
                if found.exists() and found.suffix.lower() in PLUGIN_EXTENSIONS:
                    return found.resolve()
        except Exception:
            pass

    return None


def get_bundle_binary(bundle_path: Path) -> Path | None:
    """Locate the main executable binary inside a macOS bundle."""
    macos_dir = bundle_path / "Contents" / "MacOS"
    if macos_dir.exists():
        binaries = [f for f in macos_dir.iterdir() if f.is_file() and not f.name.startswith(".")]
        if binaries:
            # Prefer binary matching bundle stem
            for b in binaries:
                if b.name.lower() == bundle_path.stem.lower():
                    return b
            return binaries[0]
    return None


def get_architecture(binary_path: Path | None) -> str:
    """Get the architecture of the binary using file command."""
    if not binary_path or not binary_path.exists():
        return "onbekend"
    try:
        res = subprocess.run(["file", str(binary_path)], capture_output=True, text=True, check=True)
        out = res.stdout
        archs = []
        if "arm64" in out:
            archs.append("arm64")
        if "x86_64" in out:
            archs.append("x86_64")
        return ", ".join(archs) if archs else out.split(":")[-1].strip()
    except Exception:
        return "onbekend"


def compute_sha256(path: Path | None) -> str:
    """Compute SHA-256 hash of a file."""
    if not path or not path.is_file():
        return "ONBEKEND"
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return "ONBEKEND"


def get_quarantine_info(target_path: Path) -> str | None:
    """Check com.apple.quarantine attribute."""
    try:
        res = subprocess.run(
            ["/usr/bin/xattr", "-p", "com.apple.quarantine", str(target_path)],
            capture_output=True,
            text=True,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return None


def get_codesign_info(target_path: Path) -> tuple[bool, str]:
    """Verify codesign signature."""
    try:
        res = subprocess.run(
            ["/usr/bin/codesign", "--verify", "--deep", "--strict", "--verbose=2", str(target_path)],
            capture_output=True,
            text=True,
        )
        msg = (res.stderr.strip() or res.stdout.strip())
        return res.returncode == 0, msg if msg else "Geldig ondertekend"
    except Exception as e:
        return False, str(e)


def get_gatekeeper_info(target_path: Path) -> tuple[bool, str]:
    """Check Gatekeeper assessment."""
    try:
        res = subprocess.run(
            ["/usr/sbin/spctl", "--assess", "--type", "execute", "-vv", str(target_path)],
            capture_output=True,
            text=True,
        )
        msg = (res.stderr.strip() or res.stdout.strip())
        return res.returncode == 0, msg if msg else "Geaccepteerd"
    except Exception as e:
        return False, str(e)


def update_ledger(ledger_path: Path, name: str, plugin_type: str, path: Path, source: str, sha256: str) -> None:
    """Update or append to components.tsv ledger."""
    lines = []
    header = "naam\ttype\tvolledig_pad\tofficiele_bron\tsha256\n"
    if ledger_path.exists():
        with open(ledger_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    if not lines:
        lines = [header]

    target_str = str(path)
    new_entry = f"{name}\t{plugin_type}\t{target_str}\t{source}\t{sha256}\n"
    
    # Check if target already present
    found = False
    new_lines = []
    for line in lines:
        parts = line.strip().split("\t")
        if len(parts) >= 3 and parts[2] == target_str:
            new_lines.append(new_entry)
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(new_entry)

    with open(ledger_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def main():
    parser = argparse.ArgumentParser(
        description="Inspect, de-quarantine, or ad-hoc sign macOS audio plugins (AU, VST3, CLAP, VST, APP)."
    )
    parser.add_argument("target", help="Path or plugin name to inspect/sign")
    parser.add_argument(
        "--action",
        choices=["inspect", "approve", "sign"],
        default="inspect",
        help="Action: inspect (read-only), approve (remove quarantine), sign (ad-hoc sign + de-quarantine)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the action without making any disk modifications",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Execute without interactive confirmation",
    )
    parser.add_argument(
        "--source",
        default="Lokaal / Onbekend",
        help="Source label for ledger registration",
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=Path(__file__).parent / "components.tsv",
        help="Path to components.tsv inventory",
    )

    args = parser.parse_args()

    # 1. Resolve Target
    target_path = find_plugin(args.target, ledger_path=args.ledger)
    if not target_path or not target_path.exists():
        print(f"FOUT: Plugin '{args.target}' niet gevonden.", file=sys.stderr)
        print("Geef het volledige pad op of controleer de naam.", file=sys.stderr)
        sys.exit(1)

    binary_path = get_bundle_binary(target_path)
    ext = target_path.suffix.lower()
    plugin_type = ext.lstrip(".").upper()
    arch = get_architecture(binary_path)
    sha = compute_sha256(binary_path)
    quarantine = get_quarantine_info(target_path)
    cs_ok, cs_msg = get_codesign_info(target_path)
    gk_ok, gk_msg = get_gatekeeper_info(target_path)

    # Output inspection header
    print(f"### Plugin Inspectie: {target_path.name}")
    print(f"- **Pad:** `{target_path}`")
    print(f"- **Formaat:** `{plugin_type}` ({ext})")
    print(f"- **Architectuur:** `{arch}`")
    print(f"- **SHA-256 binary:** `{sha}`")
    print(f"- **Quarantine:** {'⚠️ Aanwezig (' + quarantine + ')' if quarantine else '✅ Niet in quarantaine'}")
    print(f"- **Handtekening:** {'✅ ' + cs_msg if cs_ok else '❌ ' + cs_msg}")
    print(f"- **Gatekeeper:** {'✅ ' + gk_msg if gk_ok else '❌ ' + gk_msg}")

    # Logic Pro AU Note
    if plugin_type != "COMPONENT":
        sibling_au = target_path.parent / f"{target_path.stem}.component"
        if sibling_au.exists():
            print(f"- **Logic Pro AU Hint:** Sibling Audio Unit aanwezig op `{sibling_au}`.")
        else:
            print("- **Logic Pro AU Hint:** Logic Pro vereist Audio Units (.component). Dit formaat wordt door Logic Pro mogelijk niet direct geladen.")

    if args.action == "inspect":
        sys.exit(0)

    # Confirmation if interactive and not dry-run
    if not args.yes and not args.dry_run and sys.stdin.isatty():
        resp = input(f"\nWeet je zeker dat je '{args.action}' wilt uitvoeren op dit bestand? [j/N]: ")
        if resp.lower() not in {"j", "ja", "y", "yes"}:
            print("Geannuleerd.")
            sys.exit(1)

    # 2. Approve (Remove Quarantine)
    if args.action == "approve":
        if args.dry_run:
            print(f"\n[DRY RUN] Zou quarantine verwijderen van: {target_path}")
            sys.exit(0)
        if quarantine:
            subprocess.run(["/usr/bin/xattr", "-dr", "com.apple.quarantine", str(target_path)], check=True)
            print("\n✅ Quarantine succesvol verwijderd.")
        else:
            print("\nGeen quarantine attribuut gevonden.")

    # 3. Sign (Ad-hoc Sign)
    elif args.action == "sign":
        if args.dry_run:
            print(f"\n[DRY RUN] Zou ad-hoc ondertekenen met codesign en quarantine verwijderen:")
            print(f"  - Commando: /usr/bin/xattr -dr com.apple.quarantine \"{target_path}\"")
            print(f"  - Commando: /usr/bin/codesign --force --deep --sign - \"{target_path}\"")
            sys.exit(0)

        # De-quarantine first
        if quarantine:
            subprocess.run(["/usr/bin/xattr", "-dr", "com.apple.quarantine", str(target_path)], check=False)

        # Ad-hoc sign
        res = subprocess.run(
            ["/usr/bin/codesign", "--force", "--deep", "--sign", "-", str(target_path)],
            capture_output=True,
            text=True,
        )
        if res.returncode == 0:
            print("\n✅ Plugin succesvol ad-hoc ondertekend.")
        else:
            print(f"\n❌ Fout bij ondertekenen: {res.stderr.strip()}", file=sys.stderr)
            sys.exit(res.returncode)

    # Verify after modification
    new_cs_ok, new_cs_msg = get_codesign_info(target_path)
    new_quarantine = get_quarantine_info(target_path)
    print(f"- **Nacontrole Handtekening:** {'✅ ' + new_cs_msg if new_cs_ok else '❌ ' + new_cs_msg}")
    print(f"- **Nacontrole Quarantine:** {'⚠️ ' + new_quarantine if new_quarantine else '✅ Verwijderd'}")

    # Update ledger
    try:
        update_ledger(args.ledger, target_path.stem, plugin_type, target_path, args.source, sha)
        print(f"- **Inventaris:** Bijgewerkt in `{args.ledger.name}`.")
    except Exception as e:
        print(f"- **Inventaris waarschuwing:** Kon ledger niet bijwerken: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()

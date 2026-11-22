#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CACHE_FILE = ".github_maintainer_cache.json"
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "node_modules",
}


def get_readme_hash(readme_path):
    hash_sha256 = hashlib.sha256()
    with open(readme_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def check_readme(repo_path, cache):
    readme_path = repo_path / "README.md"
    if not readme_path.exists():
        return False

    stat = readme_path.stat()
    size = stat.st_size
    mtime = stat.st_mtime
    repo_str = str(repo_path)

    repo_cache = cache.get(repo_str, {})
    if repo_cache.get("readme_size") == size and repo_cache.get("readme_mtime") == mtime:
        return False  # Geen verandering

    current_hash = get_readme_hash(readme_path)
    if repo_cache.get("readme_hash") == current_hash:
        # Tyd of grootte het dalk verander agv git checkout, maar inhoud is selfde
        cache[repo_str] = {"readme_size": size, "readme_mtime": mtime, "readme_hash": current_hash}
        return False

    cache[repo_str] = {"readme_size": size, "readme_mtime": mtime, "readme_hash": current_hash}
    return True


def is_git_dirty(repo_path):
    result = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True)
    return bool(result.stdout.strip())


def one_line(text):
    """Maak vrye teks veilig vir een markdown-tabelry."""
    return " ".join(str(text).split()).replace("|", "\\|")


def should_build(git_msg, readme_changed, force_build=False):
    """Bou wanneer daar iets verander het, of wanneer die gebruiker dit forceer."""
    if force_build:
        return True
    return not (git_msg == "Reeds op datum" and not readme_changed)


def discover_repos(root_path):
    """Vind top-level repositories en slaan geneste checkouts (vendor/deps) oor."""
    repos = []
    for dirpath, dirnames, _filenames in os.walk(root_path):
        current = Path(dirpath)
        if ".git" in dirnames or (current / ".git").is_file():
            repos.append(current)
            dirnames[:] = []  # nie in 'n repo afdaal nie: geneste repos word ignored
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    return sorted(repos, key=lambda p: str(p))


def repo_eligibility(repo_path):
    """(eligible, branch-of-reden): slaat detached HEAD en repos sonder upstream oor."""
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if branch.returncode != 0:
        return False, f"Git-fout bij branchdetectie: {one_line(branch.stderr)}"
    branch_name = branch.stdout.strip()
    if branch_name in ("", "HEAD"):
        return False, "Detached HEAD (geen branch)"

    upstream = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "@{u}"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if upstream.returncode != 0:
        return False, "Geen upstream/tracking branch"
    return True, upstream.stdout.strip()


def upstream_refspec(repo_path):
    """Gerigte fetch-refspec (remote, refspec) of None wanneer config ontbreek."""
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if branch.returncode != 0:
        return None
    branch_name = branch.stdout.strip()
    if branch_name in ("", "HEAD"):
        return None

    remote = subprocess.run(
        ["git", "config", "--get", f"branch.{branch_name}.remote"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    merge = subprocess.run(
        ["git", "config", "--get", f"branch.{branch_name}.merge"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if remote.returncode != 0 or merge.returncode != 0:
        return None

    remote_name = remote.stdout.strip()
    merge_ref = merge.stdout.strip()
    if not remote_name or not merge_ref:
        return None

    if merge_ref.startswith("refs/heads/"):
        short = merge_ref[len("refs/heads/"):]
        return remote_name, f"{merge_ref}:refs/remotes/{remote_name}/{short}"
    return remote_name, merge_ref


def update_git(repo_path, dry_run):
    if dry_run:
        return "Dry-run: git fetch + fast-forward gepland", True

    fetch = subprocess.run(["git", "fetch"], cwd=repo_path, capture_output=True, text=True)
    if fetch.returncode != 0:
        # Bv. case-insensitive filesystems met conflicterende refs: haal slegs
        # die tracking-branch op, met 'n eksplisiete remote-tracking bestemming.
        fallback = upstream_refspec(repo_path)
        if fallback:
            remote, refspec = fallback
            retry = subprocess.run(
                ["git", "fetch", remote, refspec], cwd=repo_path, capture_output=True, text=True
            )
            if retry.returncode == 0:
                fetch = retry
    if fetch.returncode != 0:
        return f"Git fetch-fout: {one_line(fetch.stderr)}", False

    res = subprocess.run(
        ["git", "merge", "--ff-only"], cwd=repo_path, capture_output=True, text=True
    )
    if res.returncode == 0:
        if "Already up to date" in res.stdout or "Already up-to-date" in res.stdout:
            return "Reeds op datum", True
        return "Suksesvol bygewerk", True

    detail = one_line(res.stderr or res.stdout) or "onbekende fout"
    return f"Geen fast-forward: {detail}", False


def package_install_command(repo_path):
    """Kies die package manager op basis van packageManager-veld of lockfile."""
    package_json = repo_path / "package.json"
    manager = None
    try:
        data = json.loads(package_json.read_text())
        declared = str(data.get("packageManager", "")).split("@", 1)[0].strip()
        if declared in {"npm", "pnpm", "yarn", "bun"}:
            manager = declared
    except (OSError, ValueError):
        pass

    if manager is None:
        if (repo_path / "pnpm-lock.yaml").exists():
            manager = "pnpm"
        elif (repo_path / "yarn.lock").exists():
            manager = "yarn"
        elif (repo_path / "bun.lockb").exists() or (repo_path / "bun.lock").exists():
            manager = "bun"
        elif (repo_path / "package-lock.json").exists() or (repo_path / "npm-shrinkwrap.json").exists():
            manager = "npm"
        else:
            manager = "npm"

    return [manager, "install"]


def detect_and_build(repo_path, dry_run):
    build_cmds = []
    if (repo_path / "Cargo.toml").exists():
        build_cmds.append(["cargo", "build", "--release"])
    elif (repo_path / "CMakeLists.txt").exists():
        build_cmds.append(["cmake", "-B", "build", "-DCMAKE_BUILD_TYPE=Release"])
        build_cmds.append(["cmake", "--build", "build", "--config", "Release"])
    elif (repo_path / "package.json").exists():
        build_cmds.append(package_install_command(repo_path))
    elif (repo_path / "go.mod").exists():
        build_cmds.append(["go", "build", "./..."])

    if not build_cmds:
        return "Geen bekende boustelsel", True

    if dry_run:
        planned = ", ".join(" ".join(cmd) for cmd in build_cmds)
        return f"Dry-run: {len(build_cmds)} opdrag(te) gepland: {planned}", True

    for cmd in build_cmds:
        if shutil.which(cmd[0]) is None:
            return f"Bou-gereedschap niet gevonden: {cmd[0]}", False
        try:
            subprocess.run(cmd, cwd=repo_path, capture_output=True, check=True, timeout=300)
        except subprocess.TimeoutExpired:
            return f"Bou time-out vir {' '.join(cmd)}", False
        except subprocess.CalledProcessError as e:
            return f"Bou-fout met {' '.join(cmd)}: {one_line(e.stderr)}", False

    return "Bou suksesvol", True


def main():
    parser = argparse.ArgumentParser(description="GitHub Repo Maintainer")
    parser.add_argument("--root", type=str, help="Wortelgids met repositories", default=os.getenv("GITHUB_REPOS_ROOT", "."))
    parser.add_argument("--dry-run", action="store_true", help="Wys beplande aksies sonder om repositories te wysig")
    parser.add_argument("--force-build", action="store_true", help="Bou ook wanneer 'n repo reeds op datum is")
    args = parser.parse_args()

    root_path = Path(args.root).resolve()
    if not root_path.exists() or not root_path.is_dir():
        print(f"Gids nie gevind nie: {root_path}")
        sys.exit(1)

    cache_path = root_path / CACHE_FILE
    if cache_path.exists():
        with open(cache_path, "r") as f:
            cache = json.load(f)
    else:
        cache = {}

    repos = discover_repos(root_path)

    verslag = []
    sukses_tel = 0
    fout_tel = 0
    oorgeslaan_tel = 0

    print(f"Ontdek {len(repos)} top-level repositories in {root_path}...")

    for repo in repos:
        repo_naam = repo.name
        try:
            eligible, info = repo_eligibility(repo)
            if not eligible:
                verslag.append({"repo": repo_naam, "status": "Oorgeslaan", "rede": info})
                oorgeslaan_tel += 1
                continue

            if is_git_dirty(repo):
                verslag.append({"repo": repo_naam, "status": "Oorgeslaan", "rede": "Ongestoorde plaaslike wysigings (dirty)"})
                oorgeslaan_tel += 1
                continue

            readme_verander = check_readme(repo, cache)

            git_msg, git_sukses = update_git(repo, args.dry_run)
            if not git_sukses:
                verslag.append({"repo": repo_naam, "status": "Misluk", "rede": f"Git: {git_msg}"})
                fout_tel += 1
                continue

            if args.dry_run:
                build_msg, build_sukses = detect_and_build(repo, True)
                status = "Gepland" if build_sukses else "Misluk"
                if build_sukses:
                    sukses_tel += 1
                else:
                    fout_tel += 1
                verslag.append({
                    "repo": repo_naam,
                    "status": status,
                    "rede": f"{git_msg}. {build_msg}. README verander: {readme_verander}",
                })
                continue

            if not should_build(git_msg, readme_verander, args.force_build):
                verslag.append({"repo": repo_naam, "status": "Sukses", "rede": "Reeds op datum, geen build nodig"})
                sukses_tel += 1
                continue

            build_msg, build_sukses = detect_and_build(repo, False)
            if args.force_build:
                build_msg += " (geforceerd)"
            if build_sukses:
                verslag.append({
                    "repo": repo_naam,
                    "status": "Sukses",
                    "rede": f"{git_msg}. {build_msg}. README verander: {readme_verander}",
                })
                sukses_tel += 1
            else:
                verslag.append({"repo": repo_naam, "status": "Misluk", "rede": f"Build misluk: {build_msg}"})
                fout_tel += 1
        except Exception as exc:  # foutisolasie: een repo mag die res nie stop nie
            verslag.append({"repo": repo_naam, "status": "Misluk", "rede": f"Onverwachte fout: {exc}"})
            fout_tel += 1

    # Cache word in beide modi bewaar, sodat README-hashes ook na 'n dry-run bekend is.
    with open(cache_path, "w") as f:
        json.dump(cache, f, indent=4)

    # Skep verslag
    sukses_label = "Gepland" if args.dry_run else "Sukses"
    modus = "dry-run (geen repositories gewysig)" if args.dry_run else "uitvoering"
    md_verslag = [
        "# GitHub Repo Maintainer Verslag",
        f"**Datum:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Modus:** {modus}",
        f"**Totaal Repos:** {len(repos)} | **{sukses_label}:** {sukses_tel} | **Misluk:** {fout_tel} | **Oorgeslaan:** {oorgeslaan_tel}",
        "", "| Repository | Status | Rede |", "|---|---|---|",
    ]
    for inskrywing in verslag:
        md_verslag.append(
            f"| {one_line(inskrywing['repo'])} | {inskrywing['status']} | {one_line(inskrywing['rede'])} |"
        )

    with open(root_path / "maintainer_report.md", "w") as f:
        f.write("\n".join(md_verslag))

    print(f"Klaar. Verslag gestoor by {root_path / 'maintainer_report.md'}")


if __name__ == "__main__":
    main()

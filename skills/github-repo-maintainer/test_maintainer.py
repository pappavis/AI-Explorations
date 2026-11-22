import json
import subprocess
import tempfile
from pathlib import Path

import pytest

from github_repo_maintainer import (
    check_readme,
    detect_and_build,
    discover_repos,
    get_readme_hash,
    is_git_dirty,
    one_line,
    package_install_command,
    repo_eligibility,
    should_build,
    update_git,
    upstream_refspec,
)


def _git(path, *args):
    return subprocess.run(
        ["git", *args], cwd=path, check=True, capture_output=True, text=True
    )


def _init_repo(path):
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-q", "-b", "main")
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test")
    (path / "README.md").write_text("Hallo Wêreld")
    _git(path, "add", ".")
    _git(path, "commit", "-q", "-m", "init")


# --- bestaande README-cachetests -------------------------------------------

def test_check_readme_empty_cache():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        readme_path = repo_path / "README.md"
        readme_path.write_text("Hallo Wêreld")
        cache = {}
        verander = check_readme(repo_path, cache)
        assert verander is True
        assert str(repo_path) in cache
        assert cache[str(repo_path)]["readme_hash"] == get_readme_hash(readme_path)


def test_check_readme_no_change():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        readme_path = repo_path / "README.md"
        readme_path.write_text("Hallo Wêreld")

        cache = {}
        check_readme(repo_path, cache)

        verander = check_readme(repo_path, cache)
        assert verander is False


def test_check_readme_content_changed():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        readme_path = repo_path / "README.md"
        readme_path.write_text("Hallo Wêreld")

        cache = {}
        check_readme(repo_path, cache)

        # Verander inhoud
        readme_path.write_text("Nuwe Inhoud")
        verander = check_readme(repo_path, cache)
        assert verander is True


# --- 2. geneste repositories negeren ---------------------------------------

def test_discover_repos_skips_nested_repositories(tmp_path):
    outer = tmp_path / "outer"
    _init_repo(outer)
    inner = outer / "vendor" / "inner"
    _init_repo(inner)
    sibling = tmp_path / "sibling"
    _init_repo(sibling)
    (tmp_path / "plain").mkdir()

    found = {p.resolve() for p in discover_repos(tmp_path)}

    assert found == {outer.resolve(), sibling.resolve()}
    assert inner.resolve() not in found


def test_discover_repos_ignores_non_repositories(tmp_path):
    (tmp_path / "plain").mkdir()
    (tmp_path / "plain" / "file.txt").write_text("x")
    assert discover_repos(tmp_path) == []


# --- 1. detached HEAD / geen upstream overslaan ----------------------------

def test_repo_eligibility_rejects_detached_head(tmp_path):
    repo = tmp_path / "repo"
    _init_repo(repo)
    _git(repo, "checkout", "-q", "--detach", "HEAD")

    eligible, reason = repo_eligibility(repo)

    assert eligible is False
    assert "Detached" in reason


def test_repo_eligibility_rejects_missing_upstream(tmp_path):
    repo = tmp_path / "repo"
    _init_repo(repo)

    eligible, reason = repo_eligibility(repo)

    assert eligible is False
    assert "upstream" in reason.lower()


def test_repo_eligibility_accepts_tracking_branch(tmp_path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
    repo = tmp_path / "repo"
    _init_repo(repo)
    _git(repo, "remote", "add", "origin", str(remote))
    _git(repo, "push", "-q", "-u", "origin", "main")

    eligible, reason = repo_eligibility(repo)

    assert eligible is True
    assert "origin/main" in reason


# --- 4. package manager detecteren -----------------------------------------

@pytest.mark.parametrize(
    ("lockfile", "expected"),
    [
        ("pnpm-lock.yaml", "pnpm"),
        ("yarn.lock", "yarn"),
        ("package-lock.json", "npm"),
        ("bun.lockb", "bun"),
        (None, "npm"),
    ],
)
def test_package_install_command_detects_lockfile(tmp_path, lockfile, expected):
    (tmp_path / "package.json").write_text("{}")
    if lockfile:
        (tmp_path / lockfile).write_text("")
    assert package_install_command(tmp_path)[0] == expected


def test_package_install_command_uses_package_manager_field(tmp_path):
    (tmp_path / "package.json").write_text(json.dumps({"packageManager": "pnpm@9.0.0"}))
    assert package_install_command(tmp_path)[0] == "pnpm"


def test_detect_and_build_dry_run_does_not_execute(monkeypatch, tmp_path):
    (tmp_path / "package.json").write_text("{}")
    (tmp_path / "package-lock.json").write_text("")

    def boom(*args, **kwargs):
        raise AssertionError("build mag niet draaien tijdens dry-run")

    monkeypatch.setattr("github_repo_maintainer.subprocess.run", boom)

    message, success = detect_and_build(tmp_path, True)

    assert success is True
    assert "Dry-run" in message
    assert "npm install" in message


# --- 5. git-stderr in het rapport ------------------------------------------

class _Result:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_update_git_includes_stderr_on_failure(monkeypatch, tmp_path):
    results = iter([
        _Result(0, "", ""),
        _Result(1, "", "fatal: Not possible to fast-forward\n"),
    ])
    monkeypatch.setattr(
        "github_repo_maintainer.subprocess.run", lambda *a, **k: next(results)
    )

    message, success = update_git(tmp_path, False)

    assert success is False
    assert "Not possible to fast-forward" in message


def test_one_line_flattens_and_escapes_markdown():
    assert one_line("a\nb | c") == "a b \\| c"


# --- builds forceren en gerigte fetch-fallback ------------------------------

def test_should_build_skips_unchanged_up_to_date_repo():
    assert should_build("Reeds op datum", False, False) is False


def test_should_build_when_readme_changed():
    assert should_build("Reeds op datum", True, False) is True


def test_should_build_when_git_updated():
    assert should_build("Suksesvol bygewerk", False, False) is True


def test_should_build_force_overrides_up_to_date():
    assert should_build("Reeds op datum", False, True) is True


def test_upstream_refspec_returns_remote_and_explicit_destination(tmp_path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
    repo = tmp_path / "repo"
    _init_repo(repo)
    _git(repo, "remote", "add", "origin", str(remote))
    _git(repo, "push", "-q", "-u", "origin", "main")

    assert upstream_refspec(repo) == (
        "origin",
        "refs/heads/main:refs/remotes/origin/main",
    )


def test_update_git_retries_with_targeted_fetch(monkeypatch, tmp_path):
    results = iter([
        _Result(1, "", "case-insensitive filesystem"),
        _Result(0, "", ""),
        _Result(0, "Already up to date.", ""),
    ])
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return next(results)

    monkeypatch.setattr("github_repo_maintainer.subprocess.run", fake_run)
    monkeypatch.setattr(
        "github_repo_maintainer.upstream_refspec",
        lambda path: ("origin", "refs/heads/main:refs/remotes/origin/main"),
    )

    message, success = update_git(tmp_path, False)

    assert success is True
    assert message == "Reeds op datum"
    assert calls[1] == [
        "git",
        "fetch",
        "origin",
        "refs/heads/main:refs/remotes/origin/main",
    ]

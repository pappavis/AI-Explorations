#!/bin/bash
echo "Installeer GitHub Repo Maintainer Skill..."
DST="$HOME/.agents/skills/github-repo-maintainer"
mkdir -p "$DST"
cp SKILL.md github_repo_maintainer.py test_maintainer.py requirements.txt install.sh "$DST"/
chmod +x "$DST/github_repo_maintainer.py" "$DST/install.sh"
mkdir -p "$HOME/.claude/skills" "$HOME/.gemini/config/skills"
ln -sfn ../../.agents/skills/github-repo-maintainer "$HOME/.claude/skills/github-repo-maintainer"
ln -sfn "$DST" "$HOME/.gemini/config/skills/github-repo-maintainer"
echo "Klaar! Skill is geïnstalleer in $DST"

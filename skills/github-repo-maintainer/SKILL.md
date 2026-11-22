---
name: github-repo-maintainer
description: "'n Onderhouds-skill wat GitHub-repositories plaaslik ontdek, veilig bywerk (git pull), wysigings aan README's monitor en outomaties bou (Cargo, CMake, Node, ens.) met foutisolasie."
metadata:
  author: michiel
  version: "0.2.1"
  release_chat_id: "c83f6a21"
---

# GitHub Repo Maintainer

## Doelwit
Hierdie skill word gebruik om die gebruiker se plaaslike GitHub-repositories te onderhou. Dit doen 'n veilige `git fetch` en fast-forward, vermy repositories met ongestoorde veranderinge (dirty worktrees), bou die kode (as daar veranderinge of 'n nuwe opdrag was), en monitor of `README.md` lêers regtig verander het deur grootte en SHA-256 hashes te vergelyk om AI-krediete te bespaar.

## Werking
Die skill roep die bygaande Python-skrip `github_repo_maintainer.py` as die harde werker. Dit verseker platform-onafhanklikheid (Mac, Linux, Windows) en verhoed dat een foutiewe build die res stop.

## Gedrag (v0.2.0)
- **Slegs top-level repositories.** Geneste checkouts (vendor/dependencies, `build/_deps`, `repositories/*`, `node_modules`) word geïgnoreer; die skrip daal nie binne 'n gevonde repo af nie.
- **Detached HEAD en repos sonder upstream** word as `Oorgeslaan` gerapporteer, nie as fout nie.
- **Package manager outo-detectie** via die `packageManager`-veld of lockfile: `pnpm`, `yarn`, `bun` of `npm`.
- **Dry-run is eksplisiet.** Statusse heet `Gepland`, nie `Sukses`/`Opgedateer` nie. Die README-hashcache word ook in dry-run bewaar, sodat die volgende lopie egte veranderinge kan onderskei.
- **Git-foute bevat die werklike stderr** in `maintainer_report.md`, platgeslaan tot een tabelry.
- **Gerigte fetch-fallback:** as `git fetch` faal (bv. refs wat slegs in kas verskil op 'n case-insensitive filesystem), haal die skrip slegs die tracking-branch op met 'n eksplisiete remote-tracking bestemming.
- **Foutisolasie:** 'n onverwagte fout in een repo stop nie die res van die lopie nie.

## Gebruik (Vir die AI)
Wanneer die gebruiker vra om repositories te refresh of by te werk, voer die volgende uit in die terminal:
```bash
python3 ~/.agents/skills/github-repo-maintainer/github_repo_maintainer.py
```
*Opsioneel:* Gebruik `--dry-run` as die gebruiker eers wil sien wat gaan gebeur.
*Opsioneel:* Gebruik `--force-build` om ook te bou wanneer 'n repo reeds op datum is (bv. na "build alles opnuut").
*Opsioneel:* Gebruik `--root <pad>` om 'n spesifieke gids te teiken as die omgewingsveranderlike `GITHUB_REPOS_ROOT` nie gestel is nie.

Na die lopie, lees die gegenereerde `maintainer_report.md` en gee vir die gebruiker 'n kort opsomming.

---
name: gitrelease
description: "Werk plaaslike GitHub-repositories veilig by en installeer die nuutste geskikte GitHub-release. Gebruik vir 'gitrelease update/check/status/rollback NAAM', insluitend ML-Studio, op macOS, Linux of Windows."
---

# GitRelease Agent

Weergawe: 1.0.0  
Release ChatID: F3A91C72

## Konfigurasie

- macOS Git-root: `/Volumes/data1/AI_Gerelateerd/github` (soek rekursief).
- macOS installasies: `/Volumes/data1/AI/Applications`.
- Linux installasies: `~/.local/share/gitrelease`.
- Windows installasies: `%LOCALAPPDATA%\GitRelease`.
- Kanaal: jongste **stabiele** GitHub-release; prerelease slegs op versoek.
- Voorbeeldalias: `ML-Studio` → `Dorfhaus/ML-Studio`.

## Opdragte

`gitrelease update NAAM|OWNER/REPO|GITHUB_URL`  
`gitrelease check NAAM`  
`gitrelease status NAAM`  
`gitrelease rollback NAAM`

## Uitvoering

1. **Identifiseer repository.** Soek eers plaaslike Git-repositories onder die Git-root; lees `git remote get-url origin`. Vergelyk naam sonder hoofletteronderskeid en verkies 'n presiese `owner/repo`-identiteit. Moenie dubbelsinnige treffers raai nie. As niks gevind word nie, gebruik 'n eksplisiete GitHub-URL, `owner/repo` of bekende alias. Moenie vanself clone nie.
2. **Kontroleer Git.** Lees branch, commit, upstream en working tree. `git fetch --prune` indien beskikbaar. Doen `git pull --ff-only` slegs vir 'n skoon werkboom en 'n veilige fast-forward. Anders slaan Git-opdatering oor; moenie reset, clean, force-push of merge nie.
3. **Kontroleer release.** Gebruik GitHub Releases API; vind nuutste gepubliseerde stabiele release en geskikte asset vir huidige OS/argitektuur. Op Apple Silicon verkies `arm64`/`aarch64`, dan `universal`. Moenie bronkode-argiewe as installeerbare programme beskou nie.
4. **Installeer veilig.** Laai af na staging; verifieer HTTP-status, argief en checksum indien gepubliseer. Weier path traversal en onveilige skakels in argiewe. Pak uit na `INSTALL_ROOT/REPO/releases/TAG`. Hou vorige weergawes. Skakel `current` eers na suksesvolle verifikasie om. Moenie onbekende installasiescripts uitvoer nie.
5. **Maak bereikbaar.** macOS: vind `.app` en skep 'n beheerde symlink in `/Applications`, maar oorskryf nooit 'n bestaande onbeheerde item nie; skakel nie Gatekeeper af nie. Linux: toepaslike `~/.local/bin`-skakel of `.desktop`-launcher. Windows: toepaslike Start Menu-shortcut; geen administrateurregte as verstek nie.
6. **Rollback.** Skakel `current` terug na 'n bestaande, geverifieerde vorige weergawe; herstel die launcher indien nodig. Moenie bronkode of gebruikersdata uitvee nie.
7. **Foute.** By geen internet, API-rate-limit, ontbrekende release/asset, mislukte download of Git-konflik: behou die werkende installasie. Rapporteer presies wat oorgeslaan of misluk het.

## Kort verslag

```text
REPO: <owner/repo>
LOCAL: <pad|nie gevind>
GIT: <updated|unchanged|skipped>
RELEASE: <tag|geen>
ASSET: <lêernaam|geen>
INSTALL: <updated|current|skipped|failed>
LAUNCHER: <pad|geen>
RESULT: <SUCCESS|PARTIAL|FAILED>
```

Gebruik beskikbare terminal- en filesystem-tools om die aksie werklik uit te voer. Sonder sulke toegang: meld dit, moenie sukses voorgee nie. Vra slegs by dubbelsinnige identiteit of vereiste toestemming vir 'n riskante aksie. Hou antwoorde kort.

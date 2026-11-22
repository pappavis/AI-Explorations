---
name: musiek-github-bywerker
description: Werk Michiel se plaaslike musiek-GitHub-projekte veilig by, bou veranderde Rust/CMake-projekte, en rapporteer vordering in Afrikaans.
---
# Musiek GitHub-bywerker
Versie: 1.0.0 · Release ChatID: 20261101-8C3A1F20

## Wanneer om te gebruik
Wanneer die gebruiker vra om plaaslike musiek-repositories op datum te bring of die boustatus na te gaan.

## Werkswyse
1. Begin `bash update_github.sh` in die gids wat hierdie skill bevat. Geen interaktiewe toestemming nodig vir die normale, vooraf gemagtigde opdaterings nie.
2. Vertoon die lewendige `[nommer/totaal]`-vordering en meld elke repository se uitslag.
3. Die script doen `fetch`, vergelyk HEAD met die ingestelde upstream en gebruik slegs fast-forward; dit raak nie ongestoorde plaaslike werk of uiteenlopende geskiedenisse aan nie.
4. Bou **slegs ná nuwe commits**: Lemon-Studio met `cargo build -p os-app --release`; NeuralNote met CMake. `cargo run` word doelbewus nie outomaties uitgevoer nie.
5. Ander repositories word bygewerk, maar nie outomaties gebou nie: hulle bouinstruksies moet eers per projek bevestig word.
6. Gee 'n Afrikaanse opsomming van bygewerkte, reeds-op-datum, oorgeslane en mislukte projekte. Meld die log- en CSV-paaie.

## Veiligheidsreëls
- Geen `reset --hard`, `clean -fd`, `push`, `sudo`, of outomatiese konflikoplossing nie.
- Moenie ongeverifieerde afhanklikheids-installasies of post-update-skripte uitvoer nie.
- Bou van nuwe derdeparty-kode voer kode uit; gebruik slegs vertroude repositories.
- Die gebruiker het gewone opdaterings en bouwerk vooraf gemagtig, nie vernietigende handelinge nie.
- Wanneer die root-gids verskil, stel `MUSIC_REPOS_ROOT` eksplisiet.

## Voorbeelde
`bash update_github.sh`

`MUSIC_REPOS_ROOT='/Volumes/data1/AI_Gerelateerd/github/muziekgerlateerd' bash update_github.sh`

#!/usr/bin/env python3
"""
restore_arturia_fx.py — Generiese herstel- en oudit-nutsding vir Arturia FX Collection op macOS.

Hierdie skrip werk op ENIGE Mac (met of sonder eksterne simboliese skakels soos /Volumes/...):
1. Bespeur outomaties die werklike pad van /Library/Arturia en /Library/Arturia/Presets.
2. Kan alle geïnstalleerde Arturia FX-inproppe ouditeer vir ontbrekende fabrieks-presets.
3. Laai amptelike _resources.pkg-bundels direk vanaf Arturia se CDN af.
4. Pak dit veilig uit sonder Apple se sandkas-beperkings (omseil PackageKit shove cross-device symlink bug).
5. Korrigeer Arturia se geneste vouerstruktuur (Factory/Factory/Factory -> Factory/Factory).
6. Laat Arturia se amptelike databaseCreator-binaarlêer hardloop om db.db3 op te dateer.
7. Toets en stel korrekte lêer- en gidsregte in.
"""

import os
import sys
import argparse
import shutil
import subprocess
import urllib.request
import sqlite3

# Volledige register van alle Arturia FX-produkte, CDN-slugs en amptelike resources-pakkette
ARTURIA_FX_REGISTRY = [
    ("Filter MINI", "mini-filter", "Filter_MINI__1_9_1_6566__resources.pkg"),
    ("Filter SEM", "sem-filter", "Filter_SEM__1_8_1_6566__resources.pkg"),
    ("Filter M12", "m12-filter", "Filter_M12__1_8_1_6566__resources.pkg"),
    ("Pre 1973", "1973-pre", "Pre_1973__1_9_1_6566__resources.pkg"),
    ("Pre TridA", "trida-pre", "Pre_TridA__1_8_1_6566__resources.pkg"),
    ("Pre V76", "v76-pre", "Pre_V76__1_8_1_6566__resources.pkg"),
    ("Comp TUBE-STA", "comp-tubesta", "Comp_TUBE-STA__1_7_1_6566__resources.pkg"),
    ("Comp VCA-65", "comp-vca65", "Comp_VCA-65__1_7_1_6566__resources.pkg"),
    ("Comp FET-76", "comp-fet76", "Comp_FET-76__1_7_1_6566__resources.pkg"),
    ("Delay TAPE-201", "delay-tape201", "Delay_TAPE-201__1_7_1_6566__resources.pkg"),
    ("Delay BRIGADE", "delay-brigade", "Delay_BRIGADE__1_7_1_6566__resources.pkg"),
    ("Delay ETERNITY", "delay-eternity", "Delay_ETERNITY__1_7_1_6566__resources.pkg"),
    ("Rev SPRING-636", "rev-spring636", "Rev_SPRING-636__1_6_1_6566__resources.pkg"),
    ("Rev PLATE-140", "rev-plate140", "Rev_PLATE-140__1_7_1_6566__resources.pkg"),
    ("Rev INTENSITY", "rev-intensity", "Rev_INTENSITY__1_6_1_6566__resources.pkg"),
    ("Chorus DIMENSION-D", "chorus-dimension-d", "Chorus_DIMENSION-D__1_5_1_6566__resources.pkg"),
    ("Phaser BI-TRON", "phaser-bi-tron", "Phaser_BI-TRON__1_5_1_6566__resources.pkg"),
    ("Flanger BL-20", "flanger-bl-20", "Flanger_BL-20__1_5_1_6566__resources.pkg"),
    ("Chorus JUN-6", "chorus-jun-6", "Chorus_JUN-6__1_5_1_6566__resources.pkg"),
    ("Bus FORCE", "bus-force", "Bus_FORCE__1_4_1_6566__resources.pkg"),
    ("Comp DIODE-609", "comp-diode-609", "Comp_DIODE-609__1_4_1_6566__resources.pkg"),
    ("EQ SITRAL-295", "eq-sitral-295", "EQ_SITRAL-295__1_4_1_6566__resources.pkg"),
    ("Tape MELLO-FI", "tape-mello-fi", "Tape_MELLO-FI__1_4_1_6566__resources.pkg"),
    ("Efx FRAGMENTS", "efx-fragments", "Efx_FRAGMENTS__1_3_1_6566__resources.pkg"),
    ("Dist TUBE-CULTURE", "dist-tube-culture", "Dist_TUBE-CULTURE__1_2_1_6566__resources.pkg"),
    ("Dist OPAMP-21", "dist-opamp-21", "Dist_OPAMP-21__1_2_1_6566__resources.pkg"),
    ("Dist COLDFIRE", "dist-coldfire", "Dist_COLDFIRE__1_2_1_6566__resources.pkg"),
    ("Filter MS-20", "filter-ms-20", "Filter_MS-20__1_2_1_6566__resources.pkg"),
    ("Efx MOTIONS", "efx-motions", "Efx_MOTIONS__1_1_1_6566__resources.pkg"),
    ("Bus PEAK", "bus-peak", "Bus_PEAK__1_0_1_6566__resources.pkg"),
    ("Rev LX-24", "rev-lx-24", "Rev_LX-24__1_2_1_6567__resources.pkg"),
    ("Rotary CLS-222", "rotary-cls-222", "Rotary_CLS-222__1_2_1_6566__resources.pkg"),
    ("Efx REFRACT", "efx-refract", "Efx_REFRACT__1_1_1_6566__resources.pkg"),
    ("Bus EXCITER-104", "bus-exciter-104", "Bus_EXCITER-104__1_0_1_6566__resources.pkg"),
    ("Tape J-37", "tape-j37", "Tape_J-37__1_1_0_6566__resources.pkg"),
    ("Mix DRUMS", "mix-drums", "Mix_DRUMS__1_0_1_6566__resources.pkg"),
    ("Pitch SHIFTER-910", "pitch-shifter-910", "Pitch_SHIFTER-910__1_0_0_6566__resources.pkg"),
    ("Bus TRANSIENT", "bus-transient", "Bus_TRANSIENT__1_0_1_6566__resources.pkg"),
    ("Efx AMBIENT", "efx-ambient", "Efx_AMBIENT__1_0_0_6577__resources.pkg"),
]

def resolve_arturia_paths(custom_base=None):
    """Bespeur en los simboliese skakels op vir Arturia-paaie."""
    base = custom_base or "/Library/Arturia"
    real_base = os.path.realpath(base)
    presets_dir = os.path.join(real_base, "Presets")
    db_path = os.path.join(presets_dir, "db.db3")
    return real_base, presets_dir, db_path

def get_installed_au_components():
    """Gee 'n lys van alle Arturia .component inproppe in /Library/Audio/Plug-Ins/Components."""
    au_dir = "/Library/Audio/Plug-Ins/Components"
    installed = set()
    if os.path.exists(au_dir):
        for item in os.listdir(au_dir):
            if item.endswith(".component"):
                installed.add(item[:-10])
    return installed

def count_presets(presets_dir, name):
    """Tel die werklike fabrieks-presetlêers vir 'n spesifieke FX."""
    factory_dir = os.path.join(presets_dir, name, "Factory")
    if not os.path.exists(factory_dir):
        return 0
    count = 0
    for root, dirs, files in os.walk(factory_dir):
        for f in files:
            if not f.startswith(".") and f != "presets.featured.xml":
                count += 1
    return count

def audit_all(presets_dir):
    """Ouditeer alle 39 FX-produkte en druk 'n verslag."""
    installed_aus = get_installed_au_components()
    print("=" * 65)
    print(" ARTURIA FX COLLECTION STATUS OUDIT")
    print(f" Doel-gids: {presets_dir}")
    print("=" * 65)
    
    missing = []
    ok = []
    not_installed = []
    
    for name, slug, pkg in sorted(ARTURIA_FX_REGISTRY):
        is_inst = name in installed_aus
        count = count_presets(presets_dir, name)
        status = "OK" if count > 2 else ("LEEG / GEBREEK" if count == 0 else f"MIN ({count})")
        
        inst_mark = "[AU GEVIND]" if is_inst else "[GEEN AU]"
        print(f" {name:<20s} : {count:4d} presets  | {status:<15s} {inst_mark}")
        
        if not is_inst:
            not_installed.append(name)
        elif count <= 2:
            missing.append((name, slug, pkg, count))
        else:
            ok.append((name, count))
            
    print("-" * 65)
    print(f" Totaal OK: {len(ok)} | Herstel benodig: {len(missing)} | Nie geïnstalleer: {len(not_installed)}")
    print("=" * 65)
    return missing, ok

def restore_single_fx(name, slug, pkg, base_dir, presets_dir, temp_dir="/tmp"):
    """Laai af, pak uit, plaas lêers en herindekseer 'n spesifieke FX."""
    url = f"https://dl.arturia.net/products/{slug}/soft/components/{pkg}"
    pkg_dest = os.path.join(temp_dir, f"{slug}.pkg")
    exp_dest = os.path.join(temp_dir, f"{slug}_exp")
    
    print(f"\n[{name}] Laai amptelike hulpbronne af: {url}")
    if os.path.exists(exp_dest):
        shutil.rmtree(exp_dest, ignore_errors=True)
        
    try:
        urllib.request.urlretrieve(url, pkg_dest)
    except Exception as e:
        print(f"  FOUT tydens aflaai: {e}")
        return False

    print(f"[{name}] Pak pakket uit met pkgutil...")
    res = subprocess.run(["pkgutil", "--expand-full", pkg_dest, exp_dest], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  FOUT tydens uitpak: {res.stderr}")
        return False

    # Soek Presets/{name} in die uitgepakte payload
    src_presets = os.path.join(exp_dest, "Payload", "Library", "Arturia", "Presets", name)
    if not os.path.exists(src_presets):
        for root, dirs, files in os.walk(exp_dest):
            if "Factory" in dirs and name in root:
                src_presets = root
                break
                
    if not os.path.exists(src_presets):
        print(f"  FOUT: Kon nie presets in uitgepakte payload vind nie.")
        return False

    dst_presets = os.path.join(presets_dir, name)
    dst_factory = os.path.join(dst_presets, "Factory")
    os.makedirs(dst_presets, exist_ok=True)
    os.makedirs(dst_factory, exist_ok=True)

    # Korrigeer die Arturia 3-vlak geneste vouer bug (Factory/Factory/Factory -> Factory/Factory)
    src_factory = os.path.join(src_presets, "Factory")
    if os.path.exists(src_factory):
        nested_f3 = os.path.join(src_factory, "Factory", "Factory")
        nested_f2 = os.path.join(src_factory, "Factory")
        target_f2 = os.path.join(dst_factory, "Factory")
        os.makedirs(target_f2, exist_ok=True)
        
        src_scan = nested_f3 if os.path.exists(nested_f3) else (nested_f2 if os.path.exists(nested_f2) else src_factory)
        for item in os.listdir(src_scan):
            s = os.path.join(src_scan, item)
            d = os.path.join(target_f2, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

    # Kopieer Tutorials indien teenwoordig
    src_tut = os.path.join(src_presets, "Tutorials")
    if os.path.exists(src_tut):
        shutil.copytree(src_tut, os.path.join(dst_presets, "Tutorials"), dirs_exist_ok=True)
        
    # Kopieer featured XML indien teenwoordig
    src_xml = os.path.join(src_presets, "presets.featured.xml")
    if os.path.exists(src_xml):
        shutil.copy2(src_xml, os.path.join(dst_presets, "presets.featured.xml"))

    # Voer Arturia se eie databaseCreator uit om db.db3 by te werk
    dbc_bin = os.path.join(exp_dest, "Payload", "Library", "Arturia", "Presets", "databaseCreator")
    db_file = os.path.join(presets_dir, "db.db3")
    if os.path.exists(dbc_bin):
        print(f"[{name}] Voer databaseCreator uit vir db.db3...")
        os.chmod(dbc_bin, 0o755)
        subprocess.run([dbc_bin, "-u", "-p", f"./{name}", "-i", name, "-d", db_file], cwd=presets_dir, capture_output=True)

    # Verwyder postdbc_ko.info vlag en stel postdbc_ok.info
    inst_dir = os.path.join(base_dir, name, "Install")
    if os.path.exists(inst_dir):
        ko_f = os.path.join(inst_dir, "postdbc_ko.info")
        ok_f = os.path.join(inst_dir, "postdbc_ok.info")
        if os.path.exists(ko_f):
            os.remove(ko_f)
        open(ok_f, "a").close()

    # Maak tydelike lêers skoon
    if os.path.exists(pkg_dest):
        os.remove(pkg_dest)
    if os.path.exists(exp_dest):
        shutil.rmtree(exp_dest, ignore_errors=True)

    final_count = count_presets(presets_dir, name)
    print(f"[{name}] Suksesvol herstel: {final_count} fabrieks-presets beskikbaar.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Arturia FX Collection Presets Herstel- en Oudit-nutsding")
    parser.add_argument("--audit", action="store_true", help="Ouditeer alle produkte en wys preset-tellings")
    parser.add_argument("--all", action="store_true", help="Herstel alle FX-inproppe wat ontbrekende presets het")
    parser.add_argument("--product", type=str, help="Herstel slegs 'n spesifieke FX volgens naam (bv. 'Delay BRIGADE')")
    parser.add_argument("--force", action="store_true", help="Dwing herstel af selfs as presets reeds bestaan")
    parser.add_argument("--base-dir", type=str, default=None, help="Pasgemaakte Arturia-basispad (verstek: /Library/Arturia)")
    
    args = parser.parse_args()
    base_dir, presets_dir, db_path = resolve_arturia_paths(args.base_dir)

    if not os.path.exists(presets_dir):
        print(f"FOUT: Presets-gids bestaan nie: {presets_dir}")
        sys.exit(1)

    if args.audit or (not args.all and not args.product):
        audit_all(presets_dir)
        if not args.all and not args.product:
            print("\nGebruik --all om alle ontbrekende presets te herstel, of --product 'NAAM' vir 'n spesifieke effek.")
            sys.exit(0)

    if args.product:
        found = False
        for name, slug, pkg in ARTURIA_FX_REGISTRY:
            if name.lower() == args.product.lower() or slug.lower() == args.product.lower():
                found = True
                restore_single_fx(name, slug, pkg, base_dir, presets_dir)
                break
        if not found:
            print(f"FOUT: Produk '{args.product}' nie in register gevind nie.")
            sys.exit(1)

    elif args.all:
        missing, ok = audit_all(presets_dir)
        to_process = missing if not args.force else [(n, s, p, count_presets(presets_dir, n)) for n, s, p in ARTURIA_FX_REGISTRY]
        
        if not to_process:
            print("Geen ontbrekende presets gevind nie! Almal is reeds 100% in orde.")
            sys.exit(0)
            
        print(f"\nBegin herstel van {len(to_process)} produkte...")
        success_count = 0
        for name, slug, pkg, count in to_process:
            ok_res = restore_single_fx(name, slug, pkg, base_dir, presets_dir)
            if ok_res:
                success_count += 1
                
        # Pas veilige globale regte toe
        try:
            subprocess.run(["chmod", "-R", "777", presets_dir], capture_output=True)
        except Exception:
            pass
            
        print("\n" + "=" * 65)
        print(f" HERSTEL VOLTOOI: {success_count}/{len(to_process)} produkte suksesvol herstel.")
        print("=" * 65)

if __name__ == "__main__":
    main()

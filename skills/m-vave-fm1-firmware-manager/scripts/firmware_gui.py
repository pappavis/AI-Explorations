#!/usr/bin/env python3
# Version: 1.6.0 | Release ChatID: A61E4C92
"""Accessible firmware dashboard; firmware work stays in fm1_update.py."""
import json
import os
import queue
import re
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk


class FirmwareGUI:
    """A visual view of the existing updater, not a second updater."""

    BACKGROUND = '#0f172a'
    PANEL = '#1e293b'
    TEXT = '#f1f5f9'
    MUTED = '#a9bdd2'
    BLUE = '#38bdf8'
    GREEN = '#4ade80'
    YELLOW = '#fbbf24'

    def __init__(self, root):
        self.root = root
        self.root.title('M-VAVE Firmware Manager 1.6.0 — A61E4C92')
        self.root.geometry('1080x780')
        self.root.minsize(860, 620)
        self.root.configure(bg=self.BACKGROUND)
        self.events = queue.Queue()
        self.busy = False
        self.status_path = None
        self.rows = []
        self.filter_value = tk.StringVar(value='Alle')
        self.search_value = tk.StringVar()
        self.message = tk.StringVar(value='Kies Controleer firmware om de website te vergelijken.')
        self.counts = {}
        self._build()
        self.root.after(100, self._poll)
        self.root.after(250, lambda: self.start('status'))

    def _label(self, parent, text, size=11, color=None, bold=False):
        return tk.Label(
            parent, text=text, bg=parent.cget('bg'), fg=color or self.TEXT,
            font=('Arial', size, 'bold' if bold else 'normal'), anchor='w',
        )

    def _build(self):
        header = tk.Frame(self.root, bg=self.BACKGROUND)
        header.pack(fill='x', padx=24, pady=(19, 8))
        self._label(header, '🎹  M-VAVE Firmware Manager', 23, bold=True).pack(anchor='w')
        self._label(header, 'FM-1 / VIBE FM  •  Hardware flash: NOOIT', 11, self.MUTED).pack(anchor='w', pady=(3, 0))

        hero = tk.Frame(self.root, bg=self.PANEL, padx=18, pady=14)
        hero.pack(fill='x', padx=24, pady=10)
        self.hero_title = self._label(hero, '🔎  Firmwarestatus controleren…', 17, self.YELLOW, True)
        self.hero_title.pack(anchor='w')
        self.hero_detail = self._label(hero, 'De lokale firmwarebibliotheek wordt niet gewijzigd.', 11, self.MUTED)
        self.hero_detail.pack(anchor='w', pady=5)
        actions = tk.Frame(hero, bg=self.PANEL)
        actions.pack(anchor='w', pady=(8, 0))
        self.buttons = []
        for title, mode in (
            ('🔎 Controleer firmware', 'status'),
            ('🔄 Nu bijwerken', 'refresh'),
            ('📦 Alles opnieuw downloaden', 'update-all'),
        ):
            button = ttk.Button(actions, text=title, command=lambda action=mode: self.start(action))
            button.pack(side='left', padx=(0, 10))
            self.buttons.append(button)

        cards = tk.Frame(self.root, bg=self.BACKGROUND)
        cards.pack(fill='x', padx=24, pady=8)
        for key, title, color in (
            ('current', '🟢 ACTUEEL', self.GREEN),
            ('changed', '🟡 BIJWERKEN', self.YELLOW),
            ('new', '🔵 NIEUW', self.BLUE),
            ('unknown', '⚪ ONBEKEND', self.MUTED),
        ):
            frame = tk.Frame(cards, bg=self.PANEL, padx=16, pady=12)
            frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
            self._label(frame, title, 11, color, True).pack(anchor='w')
            count = self._label(frame, '—', 25, self.TEXT, True)
            count.pack(anchor='w', pady=(4, 0))
            self.counts[key] = count

        toolbar = tk.Frame(self.root, bg=self.BACKGROUND)
        toolbar.pack(fill='x', padx=24, pady=(8, 5))
        self._label(toolbar, 'Firmwarebibliotheek', 15, bold=True).pack(side='left')
        filter_box = ttk.Combobox(
            toolbar, textvariable=self.filter_value, state='readonly', width=17,
            values=['Alle', 'Bijwerken', 'Nieuw', 'Actueel', 'Onbekend'],
        )
        filter_box.pack(side='right', padx=(8, 0))
        filter_box.bind('<<ComboboxSelected>>', lambda _: self._filter())
        search = ttk.Entry(toolbar, textvariable=self.search_value, width=28)
        search.pack(side='right', padx=(8, 0))
        self.search_value.trace_add('write', lambda *_: self._filter())
        self._label(toolbar, 'Zoek:', 10, self.MUTED).pack(side='right')

        table_frame = tk.Frame(self.root, bg=self.BACKGROUND)
        table_frame.pack(fill='both', expand=True, padx=24, pady=(0, 6))
        columns = ('firmware', 'website', 'local', 'status')
        self.table = ttk.Treeview(table_frame, columns=columns, show='headings', height=11)
        for key, title, width in (
            ('firmware', 'Firmware', 340),
            ('website', 'Websiteversie', 150),
            ('local', 'Geïnstalleerd (manifest)', 185),
            ('status', 'Status', 150),
        ):
            self.table.heading(key, text=title)
            self.table.column(key, width=width, anchor='w')
        self.table.tag_configure('GEWIJZIGD', foreground='#b45309')
        self.table.tag_configure('NIEUW', foreground='#0369a1')
        self.table.pack(side='left', fill='both', expand=True)
        scroll = ttk.Scrollbar(table_frame, orient='vertical', command=self.table.yview)
        scroll.pack(side='right', fill='y')
        self.table.configure(yscrollcommand=scroll.set)
        self.table.bind('<<TreeviewSelect>>', self._show_source)

        bottom = tk.Frame(self.root, bg=self.BACKGROUND)
        bottom.pack(fill='x', padx=24, pady=(2, 12))
        self._label(bottom, 'Voortgang', 11, self.MUTED).pack(anchor='w')
        self.progress = ttk.Progressbar(bottom, mode='determinate', maximum=100)
        self.progress.pack(fill='x', pady=(3, 5))
        self._label(bottom, '', 1).pack_forget()
        tk.Label(bottom, textvariable=self.message, bg=self.BACKGROUND, fg=self.TEXT, anchor='w').pack(fill='x')
        details = ttk.LabelFrame(bottom, text='Technische details (optioneel)')
        details.pack(fill='x', pady=(7, 0))
        self.output = tk.Text(details, height=5, bg='#080f20', fg='#dce7f5', font=('Courier', 9), wrap='word')
        self.output.pack(fill='x', padx=6, pady=6)

    def start(self, mode):
        if self.busy:
            return
        self.busy = True
        for button in self.buttons:
            button.configure(state='disabled')
        self.progress.configure(value=0)
        self.message.set('Website en lokale firmware vergelijken…' if mode == 'status' else 'Firmware-update gestart…')
        self.output.delete('1.0', 'end')
        thread = threading.Thread(target=self._execute, args=(mode,), daemon=True)
        thread.start()

    def _execute(self, mode):
        script = Path(__file__).resolve().parent / 'fm1_update.py'
        command = [sys.executable, '-u', str(script), '--mode', mode]
        status_file = None
        if mode == 'status':
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as handle:
                status_file = Path(handle.name)
            command.extend(['--status-json', str(status_file)])
        try:
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, env={**os.environ, 'PYTHONUNBUFFERED': '1'},
            )
            for line in process.stdout:
                self.events.put(('line', line))
            code = process.wait()
            snapshot = None
            if code == 0 and status_file is not None:
                snapshot = json.loads(status_file.read_text(encoding='utf-8'))
            self.events.put(('done', (code, mode, snapshot)))
        except Exception as error:
            self.events.put(('error', str(error)))
        finally:
            if status_file is not None:
                status_file.unlink(missing_ok=True)

    def _poll(self):
        while not self.events.empty():
            kind, value = self.events.get_nowait()
            if kind == 'line':
                self.output.insert('end', value)
                self.output.see('end')
                match = re.search(r'\b(\d{1,3})%\s*\(', value)
                if match:
                    self.progress.configure(value=int(match.group(1)))
                if 'DOWNLOAD' in value or 'VALIDATION' in value or 'INSTALLATION' in value:
                    self.message.set(value.strip()[:160])
            elif kind == 'done':
                code, mode, snapshot = value
                self._finished(code, mode, snapshot)
            else:
                self._finished(2, 'error', None)
                self.output.insert('end', f'FOUT: {value}\n')
        self.root.after(100, self._poll)

    def _finished(self, code, mode, snapshot):
        self.busy = False
        for button in self.buttons:
            button.configure(state='normal')
        if code != 0:
            self.hero_title.configure(text='🔴 Controle niet voltooid', fg='#f87171')
            self.hero_detail.configure(text='Bestaande firmware niet door deze controle gewijzigd.')
            self.message.set('Bekijk de technische details. Controleer je netwerkverbinding.')
            return
        self.progress.configure(value=100)
        if snapshot:
            self._render_snapshot(snapshot)
        elif mode != 'status':
            self.hero_title.configure(text='🟢 Updateproces voltooid', fg=self.GREEN)
            self.hero_detail.configure(text='Bekijk het installatierapport. Nieuwe status wordt gecontroleerd…')
            self.message.set('Firmwarebestanden verwerkt; actuele status opnieuw ophalen.')
            self.root.after(300, lambda: self.start('status'))
        else:
            self.message.set('Statuscontrole voltooid.')

    def _render_snapshot(self, snapshot):
        fm = snapshot['counts']['FM-1']
        for key, widget in self.counts.items():
            widget.configure(text=str(fm[key]))
        pending = fm['new'] + fm['changed']
        if pending:
            self.hero_title.configure(text=f'🟡 {pending} firmware-updates beschikbaar', fg=self.YELLOW)
            self.hero_detail.configure(text='Kies Nu bijwerken om ontbrekende en gewijzigde pakketten op te halen.')
        elif fm['unknown']:
            self.hero_title.configure(text='⚪ Niet alle firmwareversies zijn verifieerbaar', fg=self.MUTED)
            self.hero_detail.configure(text='Controleer de onbekende firmware in de tabel.')
        else:
            self.hero_title.configure(text='🟢 Firmwarebibliotheek is volgens het manifest actueel', fg=self.GREEN)
            self.hero_detail.configure(text='Alle ontdekte FM-1-firmware is volgens de beschikbare metadata actueel.')
        self.rows = [row for row in snapshot['rows'] if row['kind'] == 'FM-1']
        self._filter()
        self.message.set(f'Website: {fm["website"]}  •  Manifest: {fm["local_manifest"]}  •  Hardware flash: NOOIT')

    def _filter(self):
        wanted = {
            'Alle': None, 'Bijwerken': 'GEWIJZIGD', 'Nieuw': 'NIEUW',
            'Actueel': 'ONVERANDERD', 'Onbekend': 'ONBEKEND',
        }[self.filter_value.get()]
        search = self.search_value.get().casefold().strip()
        self.table.delete(*self.table.get_children())
        for row in self.rows:
            if wanted and row['status'] != wanted:
                continue
            if search and search not in row['name'].casefold():
                continue
            self.table.insert('', 'end', values=(
                row['name'], row['website_version'], row['local_version'], row['status'],
            ), tags=(row['status'],))

    def _show_source(self, _event):
        selected = self.table.selection()
        if not selected:
            return
        name = self.table.item(selected[0], 'values')[0]
        row = next((item for item in self.rows if item['name'] == name), None)
        if row:
            self.message.set(f'{name}  •  Bron: {row["source_url"]}')


if __name__ == '__main__':
    window = tk.Tk()
    FirmwareGUI(window)
    window.mainloop()

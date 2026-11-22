#!/usr/bin/env python3
# Version: 1.6.0 | Release ChatID: A61E4C92
"""Pure, presentation-only snapshot for the firmware dashboard."""
from datetime import datetime, timezone


class DashboardLabels:
    TITLE = 'M-VAVE Firmware Manager'
    PRIMARY_ACTION = 'Nu bijwerken'


class DashboardSnapshot:
    """Translate updater's already-computed status into UI-friendly facts."""

    ORDER = {'GEWIJZIGD': 0, 'NIEUW': 1, 'ONBEKEND': 2, 'ONVERANDERD': 3}

    @classmethod
    def build(cls, entries, changes, before, target):
        counts = {}
        for kind in ('FM-1', 'SMK-37-Pro'):
            rows = [row for row in changes if row[1].startswith(kind + '/')]
            counts[kind] = {
                'website': sum(entry['kind'] == kind for entry in entries),
                'local_manifest': before.get(kind, 0),
                'new': sum(row[0] == 'NIEUW' for row in rows),
                'changed': sum(row[0] == 'GEWIJZIGD' for row in rows),
                'current': sum(row[0] == 'ONVERANDERD' for row in rows),
                'unknown': sum(row[0] == 'ONBEKEND' for row in rows),
            }
        rows = []
        for state, key, previous, website, local, url in changes:
            rows.append({
                'status': state,
                'key': key,
                'kind': key.split('/', 1)[0],
                'name': key.split('/', 1)[-1],
                'local_version': previous,
                'website_version': website,
                'source_url': url,
            })
        rows.sort(key=lambda row: (cls.ORDER.get(row['status'], 9), row['key'].casefold()))
        return {
            'schema': 1,
            'checked_at': datetime.now(timezone.utc).isoformat(),
            'target': str(target),
            'source': 'website discovery and local manifest',
            'counts': counts,
            'rows': rows,
            'hardware_flash': False,
        }

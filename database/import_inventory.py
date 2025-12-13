#!/usr/bin/env python3
"""
HomeLab Equipment Inventory Importer
Imports data from markdown hardware-inventory.md into SQLite database
"""

import sqlite3
import re
import sys
import os
from datetime import datetime
from pathlib import Path


class InventoryImporter:
    def __init__(self, db_path, markdown_path):
        self.db_path = db_path
        self.markdown_path = markdown_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        print(f"✓ Connected to database: {self.db_path}")

    def init_schema(self):
        """Initialize database schema"""
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        self.cursor.executescript(schema_sql)
        self.conn.commit()
        print("✓ Database schema initialized")

    def parse_markdown_table(self, lines, start_idx):
        """
        Parse a markdown table starting at start_idx
        Returns: (headers, rows, next_idx)
        """
        # Find header line
        if start_idx >= len(lines):
            return None, None, start_idx

        header_line = lines[start_idx].strip()
        if not header_line.startswith('|'):
            return None, None, start_idx

        # Parse headers
        headers = [h.strip() for h in header_line.split('|')[1:-1]]

        # Skip separator line
        start_idx += 1
        if start_idx >= len(lines) or not re.match(r'\|[-:\s|]+\|', lines[start_idx]):
            return headers, [], start_idx

        start_idx += 1

        # Parse rows
        rows = []
        while start_idx < len(lines):
            line = lines[start_idx].strip()
            if not line.startswith('|'):
                break

            cells = [c.strip() for c in line.split('|')[1:-1]]
            if len(cells) == len(headers):
                row_dict = dict(zip(headers, cells))
                # Filter out placeholder rows
                if not all(c in ['-', '', 'TBD'] for c in cells):
                    rows.append(row_dict)

            start_idx += 1

        return headers, rows, start_idx

    def clean_value(self, value):
        """Clean table cell value"""
        if not value or value in ['-', 'TBD', '']:
            return None
        return value

    def import_compute_servers(self, rows):
        """Import servers/workstations from Compute Hardware section"""
        count = 0
        for row in rows:
            name = self.clean_value(row.get('Name'))
            if not name:
                continue

            self.cursor.execute("""
                INSERT INTO equipment (
                    name, category, subcategory, manufacturer, model,
                    cpu, ram, storage, os, ip_address, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                'compute',
                self.clean_value(row.get('Type', '').lower()),
                None,  # manufacturer not in table
                None,  # model separate from type
                self.clean_value(row.get('CPU')),
                self.clean_value(row.get('RAM')),
                self.clean_value(row.get('Storage')),
                self.clean_value(row.get('OS')),
                self.clean_value(row.get('IP Address')),
                self.clean_value(row.get('Status', 'Active').lower()),
                self.clean_value(row.get('Notes'))
            ))
            count += 1

        self.conn.commit()
        print(f"  ✓ Imported {count} servers/workstations")

    def import_sbcs(self, rows):
        """Import Single Board Computers"""
        count = 0
        for row in rows:
            name = self.clean_value(row.get('Name'))
            model = self.clean_value(row.get('Model'))
            if not name or not model:
                continue

            self.cursor.execute("""
                INSERT INTO equipment (
                    name, category, subcategory, manufacturer, model,
                    cpu, ram, storage, os, ip_address, purpose, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                'compute',
                'sbc',
                'Raspberry Pi' if 'Raspberry Pi' in model else None,
                model,
                self.clean_value(row.get('CPU/SoC')),
                self.clean_value(row.get('RAM')),
                self.clean_value(row.get('Storage')),
                self.clean_value(row.get('OS')),
                self.clean_value(row.get('IP Address')),
                self.clean_value(row.get('Purpose')),
                self.clean_value(row.get('Notes'))
            ))
            count += 1

        self.conn.commit()
        print(f"  ✓ Imported {count} SBCs")

    def import_ai_boards(self, rows):
        """Import AI Development Boards"""
        count = 0
        for row in rows:
            name = self.clean_value(row.get('Name'))
            model = self.clean_value(row.get('Model'))
            if not name or not model:
                continue

            self.cursor.execute("""
                INSERT INTO equipment (
                    name, category, subcategory, manufacturer, model,
                    cpu, ram, storage, os, ip_address, purpose, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                'compute',
                'ai_dev_board',
                'NVIDIA' if 'Jetson' in model else None,
                model,
                self.clean_value(row.get('Compute')),
                self.clean_value(row.get('RAM')),
                self.clean_value(row.get('Storage')),
                self.clean_value(row.get('OS')),
                self.clean_value(row.get('IP Address')),
                self.clean_value(row.get('Purpose')),
                self.clean_value(row.get('Notes'))
            ))
            count += 1

        self.conn.commit()
        print(f"  ✓ Imported {count} AI dev boards")

    def import_gpus(self, rows):
        """Import GPUs/Accelerators"""
        count = 0
        for row in rows:
            name = self.clean_value(row.get('Name'))
            model = self.clean_value(row.get('Model'))
            if not name or not model:
                continue

            # Get host system to create relationship later
            host = self.clean_value(row.get('Host System'))

            self.cursor.execute("""
                INSERT INTO equipment (
                    name, category, subcategory, manufacturer, model,
                    specifications, purpose, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                'compute',
                'gpu',
                'NVIDIA' if 'NVIDIA' in model else None,
                model,
                self.clean_value(row.get('VRAM')),
                self.clean_value(row.get('Purpose')),
                f"Host: {host}. " + (self.clean_value(row.get('Notes')) or '') if host else self.clean_value(row.get('Notes'))
            ))
            count += 1

        self.conn.commit()
        print(f"  ✓ Imported {count} GPUs")

    def import_network_equipment(self, rows, subcategory):
        """Import routers, switches, access points, etc."""
        count = 0
        for row in rows:
            name = self.clean_value(row.get('Name'))
            model = self.clean_value(row.get('Model'))
            if not name or not model:
                continue

            self.cursor.execute("""
                INSERT INTO equipment (
                    name, category, subcategory, manufacturer, model,
                    ip_address, specifications, purpose, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                'networking',
                subcategory,
                'Ubiquiti' if 'UniFi' in model or 'USG' in model or 'Dream Machine' in model else None,
                model,
                self.clean_value(row.get('IP Address')),
                self.clean_value(row.get('Ports') or row.get('Bands') or row.get('Version')),
                self.clean_value(row.get('Purpose') or row.get('Coverage')),
                self.clean_value(row.get('Notes'))
            ))
            count += 1

        self.conn.commit()
        print(f"  ✓ Imported {count} {subcategory}")

    def import_storage(self, rows, subcategory):
        """Import NAS, external drives, etc."""
        count = 0
        for row in rows:
            name = self.clean_value(row.get('Name') or row.get('Location'))
            if not name:
                continue

            model = self.clean_value(row.get('Model'))
            capacity = self.clean_value(row.get('Capacity'))

            self.cursor.execute("""
                INSERT INTO equipment (
                    name, category, subcategory, manufacturer, model,
                    storage, ip_address, status, purpose, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                'storage',
                subcategory,
                'Synology' if name and 'Synology' in name else ('QNAP' if name and 'QNAP' in name else None),
                model,
                capacity,
                self.clean_value(row.get('IP Address')),
                self.clean_value(row.get('Status', 'Active').lower()),
                self.clean_value(row.get('Purpose')),
                self.clean_value(row.get('Notes'))
            ))
            count += 1

        self.conn.commit()
        print(f"  ✓ Imported {count} {subcategory}")

    def import_test_equipment_scpi(self, rows):
        """Import SCPI-enabled test equipment"""
        count = 0
        for row in rows:
            name = self.clean_value(row.get('Name'))
            model = self.clean_value(row.get('Model'))
            if not name or not model:
                continue

            # Determine subcategory from model
            subcategory = 'test_equipment'
            if 'DMM' in model or 'Multimeter' in model:
                subcategory = 'multimeter'
            elif 'MSO' in model or 'Scope' in model or 'Oscilloscope' in model:
                subcategory = 'oscilloscope'
            elif 'AWG' in model or 'DG' in model or 'Generator' in model:
                subcategory = 'signal_generator'
            elif 'DL' in model or 'Load' in model:
                subcategory = 'electronic_load'
            elif 'DP' in model or 'PSU' in name:
                subcategory = 'power_supply'

            # Extract manufacturer
            manufacturer = None
            if 'Keithley' in model:
                manufacturer = 'Keithley'
            elif 'Rigol' in model:
                manufacturer = 'Rigol'

            self.cursor.execute("""
                INSERT INTO equipment (
                    name, category, subcategory, manufacturer, model,
                    serial_number, firmware_version, ip_address, scpi_port,
                    specifications, notes, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                'test_equipment',
                subcategory,
                manufacturer,
                model,
                self.clean_value(row.get('Serial')),
                self.clean_value(row.get('Firmware')),
                self.clean_value(row.get('IP Address')),
                5025,  # Default SCPI port
                self.clean_value(row.get('Specs')),
                self.clean_value(row.get('Notes')),
                'active'
            ))
            count += 1

        self.conn.commit()
        print(f"  ✓ Imported {count} SCPI test equipment")

    def import_sdr_equipment(self, rows, subcategory):
        """Import SDR receivers and accessories"""
        count = 0
        for row in rows:
            name = self.clean_value(row.get('Name'))
            model = self.clean_value(row.get('Model'))
            if not name or not model:
                continue

            # Determine manufacturer
            manufacturer = None
            if 'HackRF' in model:
                manufacturer = 'Great Scott Gadgets'
            elif 'Nooelec' in model:
                manufacturer = 'Nooelec'

            freq_range = self.clean_value(row.get('Frequency Range') or row.get('Frequency'))
            notes = self.clean_value(row.get('Notes'))

            self.cursor.execute("""
                INSERT INTO equipment (
                    name, category, subcategory, manufacturer, model,
                    specifications, notes, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                'sdr',
                subcategory,
                manufacturer,
                model,
                f"Range: {freq_range}" if freq_range else None,
                notes,
                'active'
            ))
            count += 1

        self.conn.commit()
        print(f"  ✓ Imported {count} SDR {subcategory}")

    def import_from_markdown(self):
        """Parse markdown and import all equipment"""
        print(f"\nImporting from: {self.markdown_path}")

        with open(self.markdown_path, 'r') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Servers / Workstations
            if line == '### Servers / Workstations':
                headers, rows, i = self.parse_markdown_table(lines, i + 1)
                if rows:
                    self.import_compute_servers(rows)
                continue

            # Single Board Computers
            if line == '### Single Board Computers (SBCs)':
                headers, rows, i = self.parse_markdown_table(lines, i + 1)
                if rows:
                    self.import_sbcs(rows)
                continue

            # AI Development Boards
            if line == '### AI Development Boards (moved from AI/ML section for clarity)':
                headers, rows, i = self.parse_markdown_table(lines, i + 1)
                if rows:
                    self.import_ai_boards(rows)
                continue

            # GPUs
            if line == '### GPUs / Accelerators':
                headers, rows, i = self.parse_markdown_table(lines, i + 1)
                if rows:
                    self.import_gpus(rows)
                continue

            # Network equipment
            if line == '### Routers / Firewalls':
                headers, rows, i = self.parse_markdown_table(lines, i + 1)
                if rows:
                    self.import_network_equipment(rows, 'router')
                continue

            if line == '### Switches':
                headers, rows, i = self.parse_markdown_table(lines, i + 1)
                if rows:
                    self.import_network_equipment(rows, 'switch')
                continue

            if line == '### Access Points':
                headers, rows, i = self.parse_markdown_table(lines, i + 1)
                if rows:
                    self.import_network_equipment(rows, 'access_point')
                continue

            if line == '### Network Controllers':
                headers, rows, i = self.parse_markdown_table(lines, i + 1)
                if rows:
                    self.import_network_equipment(rows, 'controller')
                continue

            # Storage
            if line == '### NAS / Storage Servers':
                headers, rows, i = self.parse_markdown_table(lines, i + 1)
                if rows:
                    self.import_storage(rows, 'nas')
                continue

            if line == '### External Drives':
                headers, rows, i = self.parse_markdown_table(lines, i + 1)
                if rows:
                    self.import_storage(rows, 'external')
                continue

            # Test Equipment
            if line == '### Test Equipment (Network/SCPI Enabled)':
                headers, rows, i = self.parse_markdown_table(lines, i + 1)
                if rows:
                    self.import_test_equipment_scpi(rows)
                continue

            # SDR Equipment
            if line == '#### SDR Receivers':
                headers, rows, i = self.parse_markdown_table(lines, i + 1)
                if rows:
                    self.import_sdr_equipment(rows, 'receiver')
                continue

            if line == '#### SDR Accessories / Filters':
                headers, rows, i = self.parse_markdown_table(lines, i + 1)
                if rows:
                    self.import_sdr_equipment(rows, 'accessory')
                continue

            i += 1

        # Update metadata
        self.cursor.execute("""
            UPDATE metadata SET value = ?, updated_at = CURRENT_TIMESTAMP
            WHERE key = 'last_import'
        """, (datetime.now().isoformat(),))
        self.conn.commit()

    def print_summary(self):
        """Print import summary"""
        print("\n" + "="*60)
        print("IMPORT SUMMARY")
        print("="*60)

        # Count by category
        self.cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM equipment
            GROUP BY category
            ORDER BY category
        """)

        print("\nEquipment by Category:")
        total = 0
        for row in self.cursor.fetchall():
            print(f"  {row[0]:20s}: {row[1]:3d} items")
            total += row[1]
        print(f"  {'TOTAL':20s}: {total:3d} items")

        # SCPI equipment
        self.cursor.execute("SELECT COUNT(*) FROM view_scpi_equipment")
        scpi_count = self.cursor.fetchone()[0]
        print(f"\nSCPI-enabled equipment: {scpi_count} items")

        # Networked equipment
        self.cursor.execute("SELECT COUNT(*) FROM view_network_inventory")
        network_count = self.cursor.fetchone()[0]
        print(f"Networked equipment: {network_count} items")

        print("\n" + "="*60)

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("\n✓ Database connection closed")


def main():
    # Paths
    script_dir = Path(__file__).parent
    db_path = script_dir / "homelab_inventory.db"
    markdown_path = script_dir.parent / "docs" / "hardware-inventory.md"

    # Check if markdown exists
    if not markdown_path.exists():
        print(f"ERROR: Markdown file not found: {markdown_path}")
        return 1

    # Confirm before overwriting database
    if db_path.exists():
        response = input(f"\nDatabase {db_path} already exists. Overwrite? (yes/no): ")
        if response.lower() != 'yes':
            print("Import cancelled.")
            return 0
        os.remove(db_path)
        print(f"✓ Removed existing database")

    # Import
    importer = InventoryImporter(str(db_path), str(markdown_path))
    try:
        importer.connect()
        importer.init_schema()
        importer.import_from_markdown()
        importer.print_summary()
    finally:
        importer.close()

    print(f"\n✓ Import complete! Database: {db_path}")
    return 0


if __name__ == '__main__':
    sys.exit(main())

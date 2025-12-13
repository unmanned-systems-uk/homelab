#!/usr/bin/env python3
"""
HomeLab Equipment Inventory Markdown Exporter
Generates markdown documentation from the SQLite database
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime


class MarkdownExporter:
    def __init__(self, db_path, output_path):
        self.db_path = db_path
        self.output_path = output_path
        self.conn = None
        self.cursor = None
        self.output_lines = []

    def connect(self):
        """Connect to database"""
        if not Path(self.db_path).exists():
            print(f"ERROR: Database not found: {self.db_path}")
            sys.exit(1)

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def add_line(self, line=''):
        """Add a line to output"""
        self.output_lines.append(line)

    def add_table(self, headers, rows):
        """Add a markdown table"""
        if not rows:
            self.add_line("| - | - |")
            self.add_line("|---|---|")
            self.add_line()
            return

        # Create header
        header_line = '| ' + ' | '.join(headers) + ' |'
        separator = '|' + '|'.join(['---' for _ in headers]) + '|'

        self.add_line(header_line)
        self.add_line(separator)

        # Add rows
        for row in rows:
            values = [str(v) if v is not None else '-' for v in row]
            self.add_line('| ' + ' | '.join(values) + ' |')

        self.add_line()

    def export_header(self):
        """Export document header"""
        self.add_line("# HomeLab Hardware Inventory")
        self.add_line()
        self.add_line(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}")
        self.add_line("**Source:** Auto-generated from equipment database")
        self.add_line()
        self.add_line("---")
        self.add_line()

    def export_compute(self):
        """Export compute hardware section"""
        self.add_line("## 1. Compute Hardware")
        self.add_line()

        # Servers/Workstations
        self.add_line("### Servers / Workstations")
        self.cursor.execute("""
            SELECT name, subcategory as type, cpu, ram, storage, os, ip_address, status, notes
            FROM equipment
            WHERE category = 'compute' AND subcategory IN ('server', 'workstation')
            ORDER BY name
        """)
        rows = [[row[i] for i in range(len(row))] for row in self.cursor.fetchall()]
        self.add_table(['Name', 'Type', 'CPU', 'RAM', 'Storage', 'OS', 'IP Address', 'Status', 'Notes'], rows)

        # SBCs
        self.add_line("### Single Board Computers (SBCs)")
        self.cursor.execute("""
            SELECT name, model, cpu, ram, storage, os, ip_address, purpose, notes
            FROM equipment
            WHERE category = 'compute' AND subcategory = 'sbc'
            ORDER BY name
        """)
        rows = [[row[i] for i in range(len(row))] for row in self.cursor.fetchall()]
        self.add_table(['Name', 'Model', 'CPU/SoC', 'RAM', 'Storage', 'OS', 'IP Address', 'Purpose', 'Notes'], rows)

        # AI Dev Boards
        self.add_line("### AI Development Boards")
        self.cursor.execute("""
            SELECT name, model, cpu, ram, storage, os, ip_address, purpose, notes
            FROM equipment
            WHERE category = 'compute' AND subcategory = 'ai_dev_board'
            ORDER BY name
        """)
        rows = [[row[i] for i in range(len(row))] for row in self.cursor.fetchall()]
        self.add_table(['Name', 'Model', 'Compute', 'RAM', 'Storage', 'OS', 'IP Address', 'Purpose', 'Notes'], rows)

        # GPUs
        self.add_line("### GPUs / Accelerators")
        self.cursor.execute("""
            SELECT name, model, specifications, purpose, notes
            FROM equipment
            WHERE category = 'compute' AND subcategory = 'gpu'
            ORDER BY name
        """)
        rows = [[row[i] for i in range(len(row))] for row in self.cursor.fetchall()]
        self.add_table(['Name', 'Model', 'VRAM', 'Purpose', 'Notes'], rows)

        self.add_line("---")
        self.add_line()

    def export_networking(self):
        """Export networking section"""
        self.add_line("## 2. Networking")
        self.add_line()

        # Routers
        self.add_line("### Routers / Firewalls")
        self.cursor.execute("""
            SELECT name, model, specifications, ip_address, purpose, notes
            FROM equipment
            WHERE category = 'networking' AND subcategory = 'router'
            ORDER BY name
        """)
        rows = [[row[i] for i in range(len(row))] for row in self.cursor.fetchall()]
        self.add_table(['Name', 'Model', 'Ports', 'IP Address', 'Purpose', 'Notes'], rows)

        # Switches
        self.add_line("### Switches")
        self.cursor.execute("""
            SELECT name, model, specifications, ip_address, notes
            FROM equipment
            WHERE category = 'networking' AND subcategory = 'switch'
            ORDER BY name
        """)
        rows = [[row[i] for i in range(len(row))] for row in self.cursor.fetchall()]
        self.add_table(['Name', 'Model', 'Ports', 'IP Address', 'Notes'], rows)

        # Access Points
        self.add_line("### Access Points")
        self.cursor.execute("""
            SELECT name, model, specifications, ip_address, purpose, notes
            FROM equipment
            WHERE category = 'networking' AND subcategory = 'access_point'
            ORDER BY name
        """)
        rows = [[row[i] for i in range(len(row))] for row in self.cursor.fetchall()]
        self.add_table(['Name', 'Model', 'Bands', 'IP Address', 'Coverage', 'Notes'], rows)

        # Controllers
        self.add_line("### Network Controllers")
        self.cursor.execute("""
            SELECT name, model, specifications, ip_address, status, notes
            FROM equipment
            WHERE category = 'networking' AND subcategory = 'controller'
            ORDER BY name
        """)
        rows = [[row[i] for i in range(len(row))] for row in self.cursor.fetchall()]
        self.add_table(['Name', 'Model', 'Version', 'IP Address', 'Status', 'Notes'], rows)

        self.add_line("---")
        self.add_line()

    def export_storage(self):
        """Export storage section"""
        self.add_line("## 3. Storage")
        self.add_line()

        # NAS
        self.add_line("### NAS / Storage Servers")
        self.cursor.execute("""
            SELECT name, model, storage, ip_address, status, purpose, notes
            FROM equipment
            WHERE category = 'storage' AND subcategory = 'nas'
            ORDER BY name
        """)
        rows = [[row[i] for i in range(len(row))] for row in self.cursor.fetchall()]
        self.add_table(['Name', 'Model', 'Capacity', 'IP Address', 'Status', 'Purpose', 'Notes'], rows)

        # External drives
        self.add_line("### External Drives")
        self.cursor.execute("""
            SELECT name, storage, purpose, notes
            FROM equipment
            WHERE category = 'storage' AND subcategory = 'external'
            ORDER BY name
        """)
        rows = [[row[i] for i in range(len(row))] for row in self.cursor.fetchall()]
        self.add_table(['Name', 'Capacity', 'Purpose', 'Notes'], rows)

        self.add_line("---")
        self.add_line()

    def export_test_equipment(self):
        """Export test equipment section"""
        self.add_line("## 4. Test Equipment")
        self.add_line()

        self.add_line("**SCPI Network Access:** Enabled - test equipment controllable via network")
        self.add_line()

        # SCPI-enabled equipment
        self.add_line("### Network/SCPI Enabled Test Equipment")
        self.cursor.execute("""
            SELECT name, manufacturer, model, ip_address, scpi_port, serial_number,
                   firmware_version, specifications, notes
            FROM equipment
            WHERE category = 'test_equipment' AND scpi_port IS NOT NULL
            ORDER BY name
        """)
        rows = [[row[i] for i in range(len(row))] for row in self.cursor.fetchall()]
        self.add_table(['Name', 'Manufacturer', 'Model', 'IP', 'Port', 'Serial', 'Firmware', 'Specs', 'Notes'], rows)

        # Non-SCPI equipment
        self.add_line("### Other Test Equipment")
        self.cursor.execute("""
            SELECT name, manufacturer, model, specifications, status, notes
            FROM equipment
            WHERE category = 'test_equipment' AND scpi_port IS NULL
            ORDER BY name
        """)
        rows = [[row[i] for i in range(len(row))] for row in self.cursor.fetchall()]
        if rows:
            self.add_table(['Name', 'Manufacturer', 'Model', 'Specs', 'Status', 'Notes'], rows)
        else:
            self.add_line("*None currently*")
            self.add_line()

        self.add_line("---")
        self.add_line()

    def export_sdr(self):
        """Export SDR equipment section"""
        self.add_line("## 5. SDR Equipment")
        self.add_line()

        # SDR Receivers
        self.add_line("### SDR Receivers")
        self.cursor.execute("""
            SELECT name, manufacturer, model, specifications, notes
            FROM equipment
            WHERE category = 'sdr' AND subcategory = 'receiver'
            ORDER BY name
        """)
        rows = [[row[i] for i in range(len(row))] for row in self.cursor.fetchall()]
        self.add_table(['Name', 'Manufacturer', 'Model', 'Frequency Range', 'Notes'], rows)

        # SDR Accessories
        self.add_line("### SDR Accessories / Filters")
        self.cursor.execute("""
            SELECT name, manufacturer, model, specifications, notes
            FROM equipment
            WHERE category = 'sdr' AND subcategory = 'accessory'
            ORDER BY name
        """)
        rows = [[row[i] for i in range(len(row))] for row in self.cursor.fetchall()]
        self.add_table(['Name', 'Manufacturer', 'Model', 'Type/Frequency', 'Notes'], rows)

        self.add_line("---")
        self.add_line()

    def export_summary(self):
        """Export summary statistics"""
        self.add_line("## Inventory Summary")
        self.add_line()

        # Count by category
        self.cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM equipment
            WHERE status = 'active'
            GROUP BY category
            ORDER BY category
        """)

        self.add_line("### Equipment Count by Category (Active)")
        for row in self.cursor.fetchall():
            self.add_line(f"- **{row['category'].replace('_', ' ').title()}**: {row['count']} items")

        self.add_line()

        # SCPI equipment
        self.cursor.execute("SELECT COUNT(*) FROM view_scpi_equipment")
        scpi_count = self.cursor.fetchone()[0]
        self.add_line(f"- **SCPI-enabled devices**: {scpi_count}")

        # Networked equipment
        self.cursor.execute("SELECT COUNT(*) FROM view_network_inventory")
        network_count = self.cursor.fetchone()[0]
        self.add_line(f"- **Networked devices**: {network_count}")

        self.add_line()

        # Database metadata
        self.cursor.execute("SELECT value FROM metadata WHERE key = 'last_import'")
        last_import = self.cursor.fetchone()
        if last_import and last_import[0]:
            self.add_line(f"*Database last updated: {last_import[0]}*")
            self.add_line()

        self.add_line("---")
        self.add_line()

    def export_to_markdown(self):
        """Generate complete markdown document"""
        print(f"Exporting inventory to: {self.output_path}")

        self.export_header()
        self.export_compute()
        self.export_networking()
        self.export_storage()
        self.export_test_equipment()
        self.export_sdr()
        self.export_summary()

        # Write to file
        with open(self.output_path, 'w') as f:
            f.write('\n'.join(self.output_lines))

        print(f"✓ Export complete! ({len(self.output_lines)} lines)")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    # Paths
    script_dir = Path(__file__).parent
    db_path = script_dir / "homelab_inventory.db"
    output_path = script_dir.parent / "docs" / "hardware-inventory-auto.md"

    if not db_path.exists():
        print(f"ERROR: Database not found: {db_path}")
        print("Run import_inventory.py first to create the database.")
        return 1

    exporter = MarkdownExporter(str(db_path), str(output_path))
    try:
        exporter.connect()
        exporter.export_to_markdown()
    finally:
        exporter.close()

    print(f"\n✓ Markdown exported to: {output_path}")
    print("\nYou can now:")
    print(f"  - Review the auto-generated file: {output_path}")
    print(f"  - Compare with original: {script_dir.parent}/docs/hardware-inventory.md")
    print(f"  - Replace original if satisfied: mv {output_path} {script_dir.parent}/docs/hardware-inventory.md")

    return 0


if __name__ == '__main__':
    sys.exit(main())

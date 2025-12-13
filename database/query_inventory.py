#!/usr/bin/env python3
"""
HomeLab Equipment Inventory Query Tool
CLI tool for querying the equipment inventory database
"""

import sqlite3
import argparse
import sys
import json
from pathlib import Path

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False
    def tabulate(data, headers, tablefmt='grid'):
        """Fallback simple table formatting"""
        if not data:
            return "No data"

        # Simple ASCII table
        col_widths = [len(str(h)) for h in headers]
        for row in data:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)) if cell else 0)

        # Header
        output = []
        header_line = " | ".join(str(h).ljust(col_widths[i]) for i, h in enumerate(headers))
        output.append(header_line)
        output.append("-" * len(header_line))

        # Rows
        for row in data:
            row_line = " | ".join(str(row[i] if row[i] else '').ljust(col_widths[i]) for i in range(len(headers)))
            output.append(row_line)

        return "\n".join(output)


class InventoryQuery:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to database"""
        if not Path(self.db_path).exists():
            print(f"ERROR: Database not found: {self.db_path}")
            print("Run import_inventory.py first to create the database.")
            sys.exit(1)

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self.cursor = self.conn.cursor()

    def list_equipment(self, category=None, status='active', output_format='table'):
        """List all equipment, optionally filtered by category"""
        query = "SELECT id, name, category, subcategory, manufacturer, model, status FROM equipment WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY category, name"

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()

        if output_format == 'json':
            data = [dict(row) for row in rows]
            print(json.dumps(data, indent=2))
        else:
            headers = ['ID', 'Name', 'Category', 'Subcategory', 'Manufacturer', 'Model', 'Status']
            table_data = [[row[k] for k in ['id', 'name', 'category', 'subcategory', 'manufacturer', 'model', 'status']] for row in rows]
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
            print(f"\nTotal: {len(rows)} items")

    def show_details(self, equipment_id):
        """Show detailed information for a specific equipment item"""
        self.cursor.execute("SELECT * FROM equipment WHERE id = ?", (equipment_id,))
        row = self.cursor.fetchone()

        if not row:
            print(f"ERROR: Equipment ID {equipment_id} not found")
            return

        print("\n" + "="*60)
        print(f"EQUIPMENT DETAILS - ID: {equipment_id}")
        print("="*60)

        # Print all fields
        for key in row.keys():
            value = row[key]
            if value is not None and value != '':
                print(f"{key:20s}: {value}")

        # Show relationships
        self.cursor.execute("""
            SELECT relation_type, c.name as related_name, c.category
            FROM equipment_relations er
            JOIN equipment c ON er.child_id = c.id
            WHERE er.parent_id = ?
        """, (equipment_id,))
        children = self.cursor.fetchall()

        if children:
            print("\nRelationships (as parent):")
            for child in children:
                print(f"  {child['relation_type']:15s} -> {child['related_name']} ({child['category']})")

        # Show history
        self.cursor.execute("""
            SELECT event_type, event_date, description, performed_by
            FROM equipment_history
            WHERE equipment_id = ?
            ORDER BY event_date DESC
            LIMIT 5
        """, (equipment_id,))
        history = self.cursor.fetchall()

        if history:
            print("\nRecent History:")
            for event in history:
                print(f"  [{event['event_date']}] {event['event_type']}: {event['description']}")

    def search(self, term, output_format='table'):
        """Search equipment by name, model, or manufacturer"""
        query = """
            SELECT id, name, category, manufacturer, model, ip_address, status
            FROM equipment
            WHERE name LIKE ? OR model LIKE ? OR manufacturer LIKE ?
            ORDER BY category, name
        """
        search_term = f"%{term}%"
        self.cursor.execute(query, (search_term, search_term, search_term))
        rows = self.cursor.fetchall()

        if output_format == 'json':
            data = [dict(row) for row in rows]
            print(json.dumps(data, indent=2))
        else:
            if not rows:
                print(f"No equipment found matching '{term}'")
                return

            headers = ['ID', 'Name', 'Category', 'Manufacturer', 'Model', 'IP', 'Status']
            table_data = [[row[k] for k in ['id', 'name', 'category', 'manufacturer', 'model', 'ip_address', 'status']] for row in rows]
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
            print(f"\nFound: {len(rows)} items")

    def list_scpi(self, output_format='table'):
        """List all SCPI-enabled test equipment"""
        self.cursor.execute("SELECT * FROM view_scpi_equipment")
        rows = self.cursor.fetchall()

        if output_format == 'json':
            data = [dict(row) for row in rows]
            print(json.dumps(data, indent=2))
        else:
            headers = ['ID', 'Name', 'Manufacturer', 'Model', 'IP Address', 'Port', 'Serial', 'Firmware']
            table_data = [[row[k] for k in ['id', 'name', 'manufacturer', 'model', 'ip_address', 'scpi_port', 'serial_number', 'firmware_version']] for row in rows]
            print("\nSCPI-Enabled Test Equipment:")
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
            print(f"\nTotal: {len(rows)} SCPI devices")

    def list_network(self, output_format='table'):
        """List all networked equipment"""
        self.cursor.execute("SELECT * FROM view_network_inventory ORDER BY CAST(SUBSTR(ip_address, 1, INSTR(ip_address||'.', '.')-1) AS INTEGER), CAST(SUBSTR(ip_address, INSTR(ip_address, '.')+1) AS INTEGER)")
        rows = self.cursor.fetchall()

        if output_format == 'json':
            data = [dict(row) for row in rows]
            print(json.dumps(data, indent=2))
        else:
            headers = ['ID', 'Name', 'Category', 'Model', 'IP Address', 'MAC', 'Location', 'Status']
            table_data = [[row[k] for k in ['id', 'name', 'category', 'model', 'ip_address', 'mac_address', 'location', 'status']] for row in rows]
            print("\nNetworked Equipment:")
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
            print(f"\nTotal: {len(rows)} networked devices")

    def calibration_status(self, output_format='table'):
        """Show calibration status for test equipment"""
        self.cursor.execute("SELECT * FROM view_calibration_due")
        rows = self.cursor.fetchall()

        if output_format == 'json':
            data = [dict(row) for row in rows]
            print(json.dumps(data, indent=2))
        else:
            headers = ['ID', 'Name', 'Model', 'Last Cal', 'Due Date', 'Days Until Due']
            table_data = [[row[k] for k in ['id', 'name', 'model', 'last_calibrated', 'calibration_due', 'days_until_due']] for row in rows]
            print("\nCalibration Status (Due within 60 days):")
            if rows:
                print(tabulate(table_data, headers=headers, tablefmt='grid'))
            else:
                print("  No equipment requiring calibration in the next 60 days")
            print(f"\nTotal: {len(rows)} items")

    def stats(self):
        """Show database statistics"""
        print("\n" + "="*60)
        print("HOMELAB INVENTORY STATISTICS")
        print("="*60)

        # Total equipment
        self.cursor.execute("SELECT COUNT(*) FROM equipment")
        total = self.cursor.fetchone()[0]
        print(f"\nTotal Equipment: {total}")

        # By category
        self.cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM equipment
            GROUP BY category
            ORDER BY count DESC
        """)
        print("\nBy Category:")
        for row in self.cursor.fetchall():
            print(f"  {row['category']:20s}: {row['count']:3d}")

        # By status
        self.cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM equipment
            GROUP BY status
            ORDER BY count DESC
        """)
        print("\nBy Status:")
        for row in self.cursor.fetchall():
            print(f"  {row['status']:20s}: {row['count']:3d}")

        # Special categories
        self.cursor.execute("SELECT COUNT(*) FROM view_scpi_equipment")
        scpi_count = self.cursor.fetchone()[0]
        print(f"\nSCPI-enabled devices: {scpi_count}")

        self.cursor.execute("SELECT COUNT(*) FROM view_network_inventory")
        network_count = self.cursor.fetchone()[0]
        print(f"Networked devices: {network_count}")

        # Database metadata
        self.cursor.execute("SELECT * FROM metadata")
        print("\nDatabase Metadata:")
        for row in self.cursor.fetchall():
            print(f"  {row['key']:20s}: {row['value']}")

        print("="*60)

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='HomeLab Equipment Inventory Query Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                          # List all equipment
  %(prog)s list --category compute       # List compute equipment
  %(prog)s search rigol                  # Search for Rigol equipment
  %(prog)s show 5                        # Show details for equipment ID 5
  %(prog)s scpi                          # List SCPI-enabled equipment
  %(prog)s network                       # List networked equipment
  %(prog)s calibration                   # Show calibration status
  %(prog)s stats                         # Show database statistics
  %(prog)s list --format json            # Output as JSON
        """
    )

    parser.add_argument('command', choices=['list', 'search', 'show', 'scpi', 'network', 'calibration', 'stats'],
                       help='Command to execute')
    parser.add_argument('argument', nargs='?', help='Command argument (search term or equipment ID)')
    parser.add_argument('--category', '-c', help='Filter by category')
    parser.add_argument('--status', '-s', default='active', help='Filter by status (default: active)')
    parser.add_argument('--format', '-f', choices=['table', 'json'], default='table',
                       help='Output format (default: table)')
    parser.add_argument('--db', default=None, help='Database path (default: ./homelab_inventory.db)')

    args = parser.parse_args()

    # Determine database path
    if args.db:
        db_path = args.db
    else:
        db_path = Path(__file__).parent / "homelab_inventory.db"

    # Create query object
    query = InventoryQuery(str(db_path))
    try:
        query.connect()

        # Execute command
        if args.command == 'list':
            query.list_equipment(category=args.category, status=args.status, output_format=args.format)
        elif args.command == 'search':
            if not args.argument:
                parser.error("search command requires a search term")
            query.search(args.argument, output_format=args.format)
        elif args.command == 'show':
            if not args.argument:
                parser.error("show command requires an equipment ID")
            try:
                equipment_id = int(args.argument)
                query.show_details(equipment_id)
            except ValueError:
                parser.error("equipment ID must be an integer")
        elif args.command == 'scpi':
            query.list_scpi(output_format=args.format)
        elif args.command == 'network':
            query.list_network(output_format=args.format)
        elif args.command == 'calibration':
            query.calibration_status(output_format=args.format)
        elif args.command == 'stats':
            query.stats()

    finally:
        query.close()

    return 0


if __name__ == '__main__':
    sys.exit(main())

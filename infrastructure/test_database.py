#!/home/anthony/ccpm-workspace/HomeLab/.venv/bin/python3
"""
Test script for HomeLab Infrastructure Database
Verifies all core functionality including encryption.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from db import HomelabDB, CredentialEncryption


def test_encryption():
    """Test Fernet encryption/decryption."""
    print("Testing encryption module...")
    enc = CredentialEncryption()

    plaintext = "SuperSecretPassword123!"
    encrypted = enc.encrypt(plaintext)
    decrypted = enc.decrypt(encrypted)

    assert decrypted == plaintext, "Encryption/decryption failed"
    print(f"  ✓ Encryption test passed")
    print(f"    Plaintext:  {plaintext}")
    print(f"    Encrypted:  {encrypted[:40]}...")
    print(f"    Decrypted:  {decrypted}")


def test_database_operations():
    """Test database CRUD operations."""
    print("\nTesting database operations...")

    db = HomelabDB()

    # Test host operations
    hosts = db.get_hosts()
    print(f"  ✓ Hosts in database: {len(hosts)}")
    for host in hosts:
        print(f"    - {host['node_name']} ({host['ip_address']})")

    # Test VM operations
    vms = db.get_vms()
    print(f"  ✓ VMs in database: {len(vms)}")
    for vm in vms:
        print(f"    - VMID {vm['vm_id']}: {vm['name']} ({vm['status']})")

    # Test VM by ID lookup
    vm = db.get_vm_by_id(100)
    if vm:
        print(f"  ✓ VM 100 lookup: {vm['name']} - {vm['purpose']}")

    # Test credential operations
    creds = db.list_credentials()
    print(f"  ✓ Credentials in database: {len(creds)}")

    if creds:
        # Test credential retrieval (encrypted)
        first_cred = creds[0]
        cred = db.get_credential(first_cred['target_type'], first_cred['target_id'])
        print(f"  ✓ Credential decryption test:")
        print(f"    Target: {first_cred['target_type']}:{first_cred['target_id']}")
        print(f"    Username: {cred['username']}")
        print(f"    Password: {'*' * len(cred['password'])}")  # Masked

    # Test audit log
    audit_entries = db.get_audit_log(limit=5)
    print(f"  ✓ Recent audit log entries: {len(audit_entries)}")
    for entry in audit_entries:
        print(f"    [{entry['timestamp']}] {entry['action']} - {entry['user']}")

    # Test service operations
    services = db.get_services()
    print(f"  ✓ Services in database: {len(services)}")

    # Test network operations
    ips = db.get_ips()
    print(f"  ✓ IP allocations: {len(ips)}")

    db.close()


def test_security():
    """Test security features."""
    print("\nTesting security features...")

    # Check database file permissions
    db_path = Path.home() / 'ccpm-workspace' / 'HomeLab' / 'infrastructure' / 'homelab.db'
    if db_path.exists():
        import os
        stat = os.stat(db_path)
        mode = oct(stat.st_mode)[-3:]
        print(f"  ✓ Database file permissions: {mode}")
        assert mode == '600', f"Database should be 600, got {mode}"

    # Check encryption key permissions
    key_file = Path.home() / '.homelab' / '.db_key'
    if key_file.exists():
        stat = os.stat(key_file)
        mode = oct(stat.st_mode)[-3:]
        print(f"  ✓ Encryption key permissions: {mode}")
        assert mode == '600', f"Key should be 600, got {mode}"

        key_dir = key_file.parent
        stat = os.stat(key_dir)
        mode = oct(stat.st_mode)[-3:]
        print(f"  ✓ Key directory permissions: {mode}")
        assert mode == '700', f"Key directory should be 700, got {mode}"


def run_all_tests():
    """Run all test suites."""
    print("=" * 60)
    print("HomeLab Infrastructure Database - Test Suite")
    print("=" * 60)

    try:
        test_encryption()
        test_database_operations()
        test_security()

        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())

#!/usr/bin/env python3
"""
Test script to verify the undo functionality works correctly.
Creates test files, organizes them, then tests the undo feature.
"""

import os
import shutil
import tempfile
from pathlib import Path
import subprocess
import sys

def create_test_files(test_dir: Path):
    """Create test files to organize."""
    test_files = [
        ('test_image.jpg', b'fake jpg content'),
        ('document.pdf', b'fake pdf content'),
        ('script.py', b'print("hello world")'),
        ('music.mp3', b'fake audio data'),
        ('archive.zip', b'fake zip data'),
        ('readme.txt', b'This is a test file'),
    ]

    for filename, content in test_files:
        file_path = test_dir / filename
        file_path.write_bytes(content)

    print(f"✓ Created {len(test_files)} test files in {test_dir}")

def run_organizer(test_dir: Path, command: list) -> subprocess.CompletedProcess:
    """Run the file organizer with given command."""
    script_path = Path(__file__).parent / 'file_organizer.py'
    full_command = [sys.executable, str(script_path)] + command
    return subprocess.run(full_command, capture_output=True, text=True)

def test_undo_functionality():
    """Test the complete organize -> undo cycle."""
    print("🧪 Testing Undo Functionality")
    print("=" * 50)

    # Create temporary test directory
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)

        # Step 1: Create test files
        create_test_files(test_dir)

        # List original files
        original_files = list(test_dir.glob('*'))
        original_files = [f for f in original_files if f.is_file()]
        print(f"✓ Original files: {[f.name for f in original_files]}")

        # Step 2: Organize files by type
        print("\n📂 Step 2: Organizing files by type...")
        result = run_organizer(test_dir, ['organize', str(test_dir), '--by', 'type'])

        if result.returncode != 0:
            print(f"❌ Organization failed: {result.stderr}")
            return False

        print("✓ Organization completed")

        # Verify files were organized
        organized_files = list(test_dir.rglob('*'))
        organized_files = [f for f in organized_files if f.is_file() and not f.name.startswith('.')]
        print(f"✓ Files after organization: {len(organized_files)} files found")

        # Check that organized structure exists
        organized_dir = test_dir / 'organized_by_type'
        if not organized_dir.exists():
            print("❌ organized_by_type directory not created")
            return False

        # Step 3: List organization sessions
        print("\n📋 Step 3: Listing organization sessions...")
        result = run_organizer(test_dir, ['undo', str(test_dir), '--list'])

        if result.returncode != 0:
            print(f"❌ List sessions failed: {result.stderr}")
            return False

        print("✓ Sessions listed successfully")
        print("Session output:")
        print(result.stdout)

        # Extract session ID from output (simple parsing)
        session_id = None
        for line in result.stdout.split('\n'):
            if line.strip().startswith('Session ID:'):
                session_id = line.split(':', 1)[1].strip()
                break

        if not session_id:
            print("❌ Could not find session ID in output")
            return False

        print(f"✓ Found session ID: {session_id}")

        # Step 4: Test dry-run undo
        print(f"\n🔍 Step 4: Testing dry-run undo for session {session_id}...")
        result = run_organizer(test_dir, ['undo', str(test_dir), '--session', session_id, '--dry-run'])

        if result.returncode != 0:
            print(f"❌ Dry-run undo failed: {result.stderr}")
            return False

        print("✓ Dry-run undo completed")
        print("Dry-run output:")
        print(result.stdout)

        # Verify files are still in organized location (dry run shouldn't move them)
        post_dry_run_files = list(test_dir.rglob('*'))
        post_dry_run_files = [f for f in post_dry_run_files if f.is_file() and not f.name.startswith('.')]
        if len(post_dry_run_files) != len(organized_files):
            print("❌ Dry-run moved files when it shouldn't have")
            return False

        # Step 5: Actually perform undo
        print(f"\n↩️  Step 5: Actually undoing session {session_id}...")
        result = run_organizer(test_dir, ['undo', str(test_dir), '--session', session_id])

        if result.returncode != 0:
            print(f"❌ Actual undo failed: {result.stderr}")
            return False

        print("✓ Undo completed")
        print("Undo output:")
        print(result.stdout)

        # Step 6: Verify files are back in original location
        print("\n✅ Step 6: Verifying files are restored...")
        restored_files = list(test_dir.glob('*'))
        restored_files = [f for f in restored_files if f.is_file() and not f.name.startswith('.')]

        original_names = sorted([f.name for f in original_files])
        restored_names = sorted([f.name for f in restored_files])

        print(f"Original files: {original_names}")
        print(f"Restored files: {restored_names}")

        if original_names != restored_names:
            print("❌ Files were not properly restored")
            print(f"Missing: {set(original_names) - set(restored_names)}")
            print(f"Extra: {set(restored_names) - set(original_names)}")
            return False

        print("✅ All files successfully restored to original locations!")

        # Step 7: Verify log was cleaned up
        print("\n🧹 Step 7: Verifying session log cleanup...")
        result = run_organizer(test_dir, ['undo', str(test_dir), '--list'])

        if session_id in result.stdout:
            print("⚠️  Session still appears in log (may be expected if other sessions exist)")
        else:
            print("✓ Session removed from log after successful undo")

        return True

if __name__ == '__main__':
    # Change to the output directory where our file_organizer.py is located
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    success = test_undo_functionality()

    if success:
        print("\n🎉 All undo functionality tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)
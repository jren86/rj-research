#!/usr/bin/env python3
"""
Auto-upload script for RJ Research Hub.
Run after each report generation to:
1. Copy new HTML reports from reports/ to site/reports/
2. Regenerate manifest.json
3. Run: git add, commit, push
Usage: python3 upload_reports.py [commit_message]
"""
import subprocess
import sys
import os
import shutil
from datetime import datetime

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_SRC = os.path.join(os.path.dirname(SITE_DIR), "reports")
REPORTS_DST = os.path.join(SITE_DIR, "reports")

def run(cmd, cwd=SITE_DIR):
    """Run a shell command and return success."""
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [WARN] {cmd[:60]}: {result.stderr.strip()[:200]}")
        return False
    return True

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    
    print(f"=== RJ Research Hub Upload === {today} ===")
    
    # Step 1: Sync reports
    print("\n[1/4] Syncing reports...")
    count = 0
    for fname in os.listdir(REPORTS_SRC):
        if fname.endswith('.html'):
            src = os.path.join(REPORTS_SRC, fname)
            dst = os.path.join(REPORTS_DST, fname)
            if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
                shutil.copy2(src, dst)
                count += 1
                print(f"  + {fname}")
    if count == 0:
        print("  (no new reports)")
    print(f"  Total: {count} new/changed reports synced")
    
    # Step 2: Regenerate manifest
    print("\n[2/4] Regenerating manifest...")
    manifest_script = os.path.join(SITE_DIR, "generate_manifest.py")
    run(f"python3 {manifest_script}")
    print("  Done")
    
    # Step 3: Git add & commit
    msg = sys.argv[1] if len(sys.argv) > 1 else f"Auto-update: {today}"
    print(f"\n[3/4] Git commit: {msg}")
    run("git add reports/ manifest.json")
    run(f'git commit -m "{msg}"')
    print("  Done")
    
    # Step 4: Push to GitHub
    print("\n[4/4] Pushing to GitHub...")
    if run("git push origin main"):
        print("  Success! Cloudflare Pages will auto-deploy.")
    else:
        print("  Push failed. Check network or SSH key setup.")
    
    print("\n=== Done ===")

if __name__ == "__main__":
    main()

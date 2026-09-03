#!/usr/bin/env python3
"""
IT8101/IT8102/IT8103/IT8106 repo cleanup script.

WHAT THIS DOES
--------------
Run this from INSIDE your local clone of MIT_EXAM_2026 (the folder that
contains MIT_DOC). It will:
  1. Create a clean course-based folder structure at the repo root:
       IT8101 Research Methods and Skills/
       IT8102 Technology Management/
       IT8103 Cyber Security/
       IT8106 Ubiquitous Computing and Intelligent Systems/
     each with "course material", "Research papers", "assignment 1",
     "assignment 2" subfolders.
  2. Copy every file from the old messy MIT_DOC tree into its correct new
     home, SKIPPING byte-identical duplicates (only one copy is kept).
  3. Skip files you had already marked for deletion (filenames starting
     with "zz DUPLICATE" or "zz OUTDATED").
  4. Leave the OLD "MIT_DOC" folder untouched (nothing is deleted from
     your working copy) - you review the new folders, and once you're
     happy, delete MIT_DOC yourself and commit.

WHAT THIS DOES NOT DO
----------------------
- It does NOT touch git at all (no add/commit/push). You run
  `git add`, `git commit`, `git push` yourself afterwards, using your own
  already-configured GitHub credentials. This script never sees or needs
  any password/token.
- It does NOT delete anything. It only copies into new folders.

HOW TO RUN
----------
  cd /path/to/your/local/MIT_EXAM_2026
  python3 reorganize_and_push.py

Then, if the result looks right:
  git rm -r "MIT_DOC"          # optional - only if you want the old copy gone
  git add -A
  git commit -m "Reorganize repo into IT8101/IT8102/IT8103/IT8106 course folders; remove duplicate files"
  git push
"""

import os
import shutil
import hashlib

REPO_ROOT = os.getcwd()
SRC = os.path.join(REPO_ROOT, "MIT_DOC")

IT8101 = "IT8101 Research Methods and Skills"
IT8102 = "IT8102 Technology Management"
IT8103 = "IT8103 Cyber Security"
IT8106 = "IT8106 Ubiquitous Computing and Intelligent Systems"

if not os.path.isdir(SRC):
    print(f"ERROR: could not find '{SRC}'.")
    print("Make sure you run this script from the root of your MIT_EXAM_2026 clone")
    print("(the folder that directly contains the 'MIT_DOC' folder).")
    raise SystemExit(1)

for course in [IT8101, IT8102, IT8103, IT8106]:
    os.makedirs(os.path.join(REPO_ROOT, course, "course material"), exist_ok=True)
    os.makedirs(os.path.join(REPO_ROOT, course, "assignment 1"), exist_ok=True)
    os.makedirs(os.path.join(REPO_ROOT, course, "assignment 2"), exist_ok=True)
os.makedirs(os.path.join(REPO_ROOT, IT8101, "Research papers"), exist_ok=True)
os.makedirs(os.path.join(REPO_ROOT, IT8106, "Research papers"), exist_ok=True)

seen_hashes = {}
copied, skipped_dup, skipped_marked = [], [], []


def file_hash(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_unique(src_path, dest_path):
    h = file_hash(src_path)
    if h in seen_hashes:
        skipped_dup.append((src_path, seen_hashes[h]))
        return
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.copy2(src_path, dest_path)
    seen_hashes[h] = dest_path
    copied.append((src_path, dest_path))


def find(*parts):
    return os.path.join(SRC, *parts)


# 1. IT8101 course docx/pdf -> "course material"
for fname in ["IT8101 Research Methods and Skills.docx", "IT8101 Research Methods and Skills.pdf"]:
    p = find(fname)
    if os.path.exists(p):
        copy_unique(p, os.path.join(REPO_ROOT, IT8101, "course material", fname))

# 2. IT8101 assessment format guides -> assignment 1
for fname in [
    "IT8101 Assessment 1 - FORMAT GUIDE (English Version).gdoc",
    "IT8101 Assessment 1 - FORMAT GUIDE (Structure, Sections, What to Write).gdoc",
]:
    p = find(fname)
    if os.path.exists(p):
        copy_unique(p, os.path.join(REPO_ROOT, IT8101, "assignment 1", fname))

# 3. IT8101 research papers (BLE security papers + matrices)
for candidate in ["IT8101 Research Method and Skill/Reserach paper ", "IT8101 Research Method and Skill/Reserach paper"]:
    research_dir = find(candidate)
    if os.path.isdir(research_dir):
        for root, dirs, files in os.walk(research_dir):
            for f in files:
                if f == ".DS_Store":
                    continue
                low = f.lower()
                if low.startswith("zz duplicate") or low.startswith("zz outdated"):
                    skipped_marked.append(os.path.join(root, f))
                    continue
                copy_unique(os.path.join(root, f), os.path.join(REPO_ROOT, IT8101, "Research papers", f))
        break

# 4. IT8106 course docx/pdf -> "course material"
for fname in ["IT8106 Ubiquitous Computing and Intelligent Systems.docx", "IT8106 Ubiquitous Computing and Intelligent Systems.pdf"]:
    p = find(fname)
    if os.path.exists(p):
        copy_unique(p, os.path.join(REPO_ROOT, IT8106, "course material", fname))

# 5. IT8106 assessment format guides -> assignment 1
for fname in [
    "IT8106 Assessment 1 - FORMAT GUIDE (English Version).gdoc",
    "IT8106 Assessment 1 - FORMAT GUIDE (Structure, Sections, What to Write).gdoc",
]:
    p = find(fname)
    if os.path.exists(p):
        copy_unique(p, os.path.join(REPO_ROOT, IT8106, "assignment 1", fname))

# 6. IT8106 IoT research papers (both duplicate locations, deduped)
for candidate in [
    "IOT Research paper",
    os.path.join("IT8106 Ubiquitous Computing and Intelligent Systems ", "IOT Research paper"),
    os.path.join("IT8106 Ubiquitous Computing and Intelligent Systems", "IOT Research paper"),
]:
    research_dir = find(candidate)
    if not os.path.isdir(research_dir):
        continue
    for root, dirs, files in os.walk(research_dir):
        rel = os.path.relpath(root, research_dir)
        for f in files:
            if f == ".DS_Store":
                continue
            src = os.path.join(root, f)
            dest = (
                os.path.join(REPO_ROOT, IT8106, "Research papers", f)
                if rel == "."
                else os.path.join(REPO_ROOT, IT8106, "Research papers", rel, f)
            )
            copy_unique(src, dest)

# 7. Cross-course planning doc -> repo root
p = find("PLAN OF ACTION - IT8101 + IT8106 (17 Aug - 4 Sept 2026).gdoc")
if os.path.exists(p):
    copy_unique(p, os.path.join(REPO_ROOT, os.path.basename(p)))

# 8. Drop the IT8106 IoT Paper Matrix deliverable into assignment 1 if present anywhere in the repo
for root, dirs, files in os.walk(SRC):
    for f in files:
        if f == "IT8106_IoT_Paper_Matrix.xlsx":
            copy_unique(os.path.join(root, f), os.path.join(REPO_ROOT, IT8106, "assignment 1", f))

print("=== DONE ===")
print(f"Unique files copied:              {len(copied)}")
print(f"Duplicate files skipped:          {len(skipped_dup)}")
print(f"User-marked-delete files skipped: {len(skipped_marked)}")
print()
print("Review the new folders, then run:")
print('  git rm -r "MIT_DOC"   # optional, only if you want the old messy copy removed')
print("  git add -A")
print('  git commit -m "Reorganize into IT8101/IT8102/IT8103/IT8106 course folders; dedupe files"')
print("  git push")
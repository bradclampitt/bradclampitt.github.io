# Rollback Plan for GitHub Profile Deployments

This document describes how to safely push updates to your live GitHub Profile site and how to roll back if something goes wrong.

## Your Existing Safety Net

- **Release "Archived original Github Profile v1"** (Oct 3, 2025) is your v1 backup. You can always restore the site to that state using the steps below.

## Before You Push (Recommended)

1. **Create a tag of current live state** (optional but recommended)  
   On your machine, with a clean connection to GitHub:
   ```bash
   git fetch origin
   # Replace main with master if your default branch is master
   git tag live-before-v2-push origin/main
   git push origin live-before-v2-push
   ```
   This gives you a named restore point for "exactly what is live right now" in case it has changed since the October 2025 release.

2. **Confirm default branch**  
   In GitHub: **Settings → Pages** (or **Code** view). Note whether the site is built from `main` or `master` (or another branch). You will push your updates to that branch.

## Push Workflow

From your project directory, on branch `cleanup-old-files`:

```bash
# 1. Stage everything that should go up (respects .gitignore)
git add -A

# 2. Review what will be committed (optional)
git status

# 3. Commit with a clear message
git commit -m "Deploy v2: SQLite/sql.js profile, cleanup, static pages for GitHub Pages"

# 4. Push your branch
git push -u origin cleanup-old-files
```

Then on GitHub:

- Either **merge `cleanup-old-files` into your default branch** (e.g. `main`) via a Pull Request, or  
- If you prefer to update the default branch directly:  
  ```bash
  git checkout main    # or master
  git merge cleanup-old-files
  git push origin main # or master
  ```

GitHub Pages will rebuild from the default branch. Give it a few minutes, then open your profile URL and check key pages (home, blog, documents, etc.).

## If Something Breaks – Rollback Options

### Option A: Revert to “live before this push” (if you created the tag)

```bash
git fetch origin
git checkout main   # or your default branch
git reset --hard origin/live-before-v2-push
git push origin main --force
```

**Warning:** `--force` rewrites history on `main`. Only do this if you are sure and that branch is the one used for Pages.

### Option B: Revert to the October 2025 v1 release

1. On GitHub: **Releases → "Archived original Github Profile v1"**.
2. Download **Source code (zip)** or **Source code (tar.gz)**.
3. In a new folder, extract the archive, then:
   ```bash
   cd <extracted-folder>
   git init
   git remote add origin git@github.com:bradclampitt/bradclampitt.github.io.git
   git add -A
   git commit -m "Rollback to v1 archive"
   git push origin main --force
   ```
   Or, if you have the v1 commit in your repo, you can tag it and reset:
   ```bash
   git fetch origin
   git checkout main
   git reset --hard <commit-hash-from-oct-2025-release>
   git push origin main --force
   ```

### Option C: Revert only the last commit (keep history)

If the problem is just the latest commit and you haven’t pushed more commits after it:

```bash
git revert HEAD --no-edit
git push origin main
```

This adds a new commit that undoes the last one; no force push.

## After a Successful Push

- Add new blog posts, documents, and other content as normal (small commits and pushes).
- For future big changes, consider creating a release or tag before deploying so you always have a named rollback point.

---
name: feedback-work-in-repo-not-tmp
description: Keep edits inside ~/git/grasshopper; if worktree isolation is forced, put the worktree next to the repo and say so up front
metadata:
  type: feedback
---

Do not park this user's code in `/tmp`. Work lands in `~/git/grasshopper/`.

**Why:** On 2026-08-28 a write guard ("bgIsolation") refused Edit/Write against the shared
checkout and required a linked git worktree. I created it at `/tmp/gh-gui-settings`, finished
the whole feature there, and only mentioned the location in the final summary. The user pushed
back: "You placed the new code in /tmp. Why not in ~/git/grasshopper/gui?" A `/tmp` path is
lost on reboot and makes the change feel detached from the project.

**How to apply:** If the isolation guard trips, (1) create the worktree adjacent to the repo,
e.g. `~/git/grasshopper-wt/<branch>`, not in `/tmp`; (2) say at the *start* of the response that
edits are going to a worktree and will need merging, not as a footnote at the end; (3) offer to
merge back to `master` as part of the same task rather than leaving it for the user. Cleanup
after merging: `git worktree remove <path> && git branch -d <branch>`.

Related: [[user-settings-profiles]]

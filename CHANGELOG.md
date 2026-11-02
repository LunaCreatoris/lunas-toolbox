# Changelog

Rules of this file:

- Every change gets one line, in English, written for someone reading the history: what changed, not how.
- Newest first. Entries sit under a period heading (`## YYYY-MM`), then under the area they touch:
  `### repository` (the layout and the root files), `### rules` (`claude/CLAUDE.md`) or `### usage` (the usage
  gate, which also keeps its own changelog). Older periods keep the areas they were written under, some of which
  no longer exist.
- Each line carries its branch name (merge request links would expose the private remote), and the decision it
  implements when there is one.
- Breaking changes, removals and migrations start with **Breaking**, **Removed** or **Migration**, and say what
  the reader has to do.

## 2026-11

### repository

- **Removed**: the home-made agent factory, its plugins, guards, shared tooling and register (`agent-factory/`,
  `.claude-plugin/`, `shared/`, `wiki/`, the root justfile and the root Python configuration). Use the third-party
  skills listed in `claude/CLAUDE.md` instead; the old content stays in git history (`chore/cleanup`).
- Changelog lines carry their branch name rather than a merge request link, which would expose the private remote
  (`chore/cleanup`).
- The repository is now two folders, `usage/` and `claude/`; the README is a short index of them and names no
  remote (`chore/cleanup`).

### rules

- The usage gate says how to reach the tool: `just usage/usage` from the project's root, with the `usage/` folder
  copied there and `just setup` run once inside it (`chore/cleanup`).
- **Migration**: `CLAUDE.md` moved to `claude/CLAUDE.md`; copy it to a project's root to use it (`chore/cleanup`).
- The Docker lock is retired: agents may run Docker-heavy commands in parallel. A usage gate is added to the
  coordination rules, and agents, the orchestrator included, push only when the user asks in their own words
  (`chore/cleanup`).

### usage

- `just setup-test` installs the pinned pytest the tests need, so `just test` works on a clean machine after it
  (`chore/cleanup`).
- The pytest pin moved into the folder (`usage/requirements.txt`), and the folder's wording no longer points at the
  removed tooling or at a remote (`chore/cleanup`).

## 2026-10

### repository

- The register records that agents reach the call centre and each other through the orchestrator, which relays
  (D-029) (`main`).
- The D-023 paragraph of the register is reflowed, same wording (`main`).
- After the review rounds, the expertise skills stand at: `vue3-frontend` 1.2.0, `web-quality` 1.2.0,
  `web-ui-design` 1.3.0, `goldens` 1.1.0, `just-recipes` 1.3.0, `os-neutral` 1.2.0, `testing` 1.3.0; D-023 now names
  a "hit your limit" message as the stop, a warning below the stop level only prompting a reading (`main`).
- Merges are gated on a detached merge commit before the target moves, and golden conflicts never resolve inside
  a merge (D-028, amended) (`main`).
- The register records the choices of the first review round, and `git-flow` lets a merge resolve a conflict
  confined to changelog lines or a generated file (D-028) (`main`).
- The register records that subagents may write the coordination files of the main checkout (D-027)
  (`main`).
- One folder per tool: `agent-factory/` (plugins, guards, template, credits, checks, eval, authoring docs),
  `usage/` (the usage gate, self-contained and portable) and `shared/` (what the root needs); the root justfile
  discovers the tool folders, and `just tool <name> <recipe>` runs one (D-020, D-021, D-022). **Migration**:
  `tools/usage.py`, `tools/platform_dirs.py` and `tools/usage-sdk/` now live in `usage/` (`usage/usage.py`,
  `usage/platform_dirs.py`, `usage/sdk/`); replace any copy taken from the old paths with the whole `usage/`
  folder, then run `just setup` and `just usage` inside it. Root recipes moved: `just check-skills`, `just credits`,
  `just eval`, `just expertise`, `just guards-install` and `just changelog-check` run from `agent-factory/` (or as
  `just tool agent-factory <recipe>`), and `just usage` from `usage/` (or `just tool usage usage`) (`main`).

### luna-backend

- Polish after review: `create_app` takes an optional `on_ready` callback backing `POST /api/ready`, matching the
  desktop shell, and the swap into `dist/` stages under a fresh `.new-<n>` name instead of deleting a leftover;
  `python-backend` and `packaging` now at 1.2.0 (`desktop-pywebview` stays at 1.1.0) (`review/polish`).
- `python-backend`, `desktop-pywebview` and `packaging` are corrected after review: unexpected errors are caught
  by an outermost middleware so the trace is logged once in the real server log, contract tests fail on an empty
  case list, "show in folder" on Windows keeps a spaced path intact, the ready callback goes to `create_app`
  instead of a frozen context, the built product is named rather than guessed, the build guard sees extension
  modules, and the swap into `dist/` copies under a temporary name first (`review/fix-backend-tooling`).
- `luna-backend` now teaches the Python desktop stack: `python-backend` (FastAPI app factory with local guards in a
  fixed order, lifespan, context dependencies, strict Pydantic v2 models, settings files set aside when unreadable,
  one error body, features as packages, pytest with shared contract fixtures), `desktop-pywebview` (hidden window
  shown on a bounded ready signal, one channel with an envelope, stable local port, platform backends behind one
  function each) and `packaging` (generic PyInstaller spec from a checked build context, onedir `.app` on macOS and
  onefile `.exe` on Windows, build guard, workshop then swap, icons derived from a provided source)
  (`skills/backend`).

### luna-tooling

- Polish after review: a rerun that reports a test failure after a crash is a real failure, and bisection shows how
  a new out-of-tree test is copied into each commit; `debugging` now at 1.2.0 (`skill-writing` stays at 1.1.0)
  (`review/polish`).
- `debugging` and `skill-writing` are tightened after review: a test believed wrong changes only once the call
  centre agrees, every code change tried counts as a hypothesis, a second infrastructure crash goes to the
  orchestrator, bisection skips crashed commits; `skill-writing` points to `agent-factory/wiki/authoring.md`, says
  its paths and recipes are relative to `agent-factory/`, and gains red-flags rows (`review/fix-backend-tooling`).
- `luna-tooling` now offers its two skills: `debugging`, a discipline that holds under pressure (reproduce, capture
  the bug in a failing test, one hypothesis at a time, fix at the root cause, stop after three failed hypotheses,
  never hide a flake), with boundary probes, bisection and the OS and network share traps to suspect; and
  `skill-writing`, how to add or change a skill of this marketplace, from traced excuses to the form that answers
  each one, descriptions, checks and the fresh-agent review (`skills/tooling`).

### luna-frontend

- `web-ui-design` 1.3.0: with no charter, the direction note sets interface colours only; brand colours (the
  product's accent, the logo's colours) are asked for as assets, with no stand-in committed meanwhile
  (`review/polish-2`).
- Second review fixes: component tests fake only the clock (full fake timers only where a test drives them), a
  system font stack is never used since every screen gets goldens, new screens add their golden, and DevTools live
  metrics count interactions performed by hand (`review/fix-frontend-quality-r2`).
- Review fixes: project conventions no longer override the hard rules, a toolchain change outside the brief goes
  to the coordinator, fonts are shipped web fonts (no system stack where goldens apply), emoji and glyphs count as
  icon stand-ins, accessibility exceptions need a register entry and a reviewer, a missing browser image is built
  or reported as a blocker, and the INP, async setup, event and mount helper notes are corrected
  (`review/fix-frontend-quality`).

- The three frontend skills are written: `vue3-frontend` (strict TypeScript Vue 3 components, composables, state,
  routing, tokens, keyboard behaviour, Vitest tests and goldens, with starting configs and a pitfalls index),
  `web-ui-design` (working from a charter or a recorded direction, tokens, every state designed, motion with a
  purpose, missing brand assets asked for, a full interface checklist) and `web-quality` (WCAG 2.2 AA including
  its new criteria, Core Web Vitals thresholds and budgets, measured verdicts and an audit format); the plugin now
  depends on `luna-quality` for its testing and goldens skills (`skills/frontend`).
### luna-quality

- `just-recipes` 1.3.0 and `testing` 1.3.0: containerised steps mount the report folder writable and run as the
  host user through one platform function, a Docker crash is rerun once before escalating, mutation runs cover
  the changed files only, and each disabled equivalent mutant names its behaviour and is listed in the report
  (`review/polish-2`).
- Second review fixes: a test judged wrong changes only once the call centre agrees, mutation runs are time boxed,
  Docker mounts take the native path and refuse a comma, and safe file names are capped at 255 bytes
  (`review/fix-frontend-quality-r2`).
- Review fixes: the last Docker lock wording is gone (D-018), the recipe shell example passes Ctrl-C to the child
  and returns 127 for a missing program, global fake timers fake only the clock, a judged-wrong test is fixed in its
  own commit against the spec, every changed golden is explained in the report, safe file names stay unreserved
  with an extension, and the path, mutation and Docker mount notes are tightened (`review/fix-frontend-quality`).

- `luna-quality` now teaches its four expertise skills in full: `testing` (test first, strict pytest and Vitest
  settings, fakes and shared contract fixtures, property-based and mutation testing, flaky tests as bugs),
  `goldens` (byte-deterministic Playwright captures in a pinned Docker image, driven by a screen manifest, with a
  determinism checklist and a stability proof), `os-neutral` (paths, platform folders, safe names, LF, commands,
  and OS exceptions behind one function) and `just-recipes` (a Python recipe shell, discovery, containerised steps
  under the Docker lock, justfile shape tests) (`skills/quality`).
### luna-factory

- Polish after the review rounds: subagents reach each other only through the orchestrator (briefs, call-centre
  relays), a coder's resume note always travels in its report, the scope hook's cwd limit is stated, the hook test
  covers the `.coordination` path itself, researchers use anonymous web access only, the research master may brief
  from leak-checked reports, and a "hit your limit" message (not an 85% warning) stops the line; skills now at
  `factory` and `coder` 1.3.0, `research-master`, `researcher`, `archaeologist-master`, `call-centre`, `manager`
  and `usage` 1.2.0 (the review rounds left `breaker`, `git-flow`, `plan-mixer` and `reviewer` at 1.2.0,
  `archaeologist`, `planner` and `terse` at 1.1.0) (`review/polish`).
- `git-flow` 1.3.0: a conflict resolved inside a merge is committed before the gate runs on it, and a conflicted
  hand-built merge tree is never resolved in place (`review/polish-2`).
- The build roles close the gaps of their second review: git-flow builds each merge commit on a detached target
  and fast-forwards the target only once the gate on that commit is green, so goldens compare with the merged HEAD;
  golden conflicts go to a fresh coder, never resolved in the merge; a changed test cites its spec in its own commit,
  checked by the reviewer in the history; the breaker reports passing tests instead of committing them (D-016,
  D-028) (`review/fix-build-r2`).
- The build roles close the gaps of their first review: the coder reports each test's red failure line, stops on a
  red baseline, changes a handed-over test only with agreement, keeps every write (Bash included) in scope, sticks
  to the plan and stops cleanly at 95%; the breaker treats a missing seam as a hole and proves "not applicable"
  with code evidence; the reviewer judges the whole diff and never signs off on a "not verified" item; git-flow
  merges with `--no-commit` so the gate runs before the merge commit (D-015, D-016, D-023) (`review/fix-build`).
- The scope hook now lets subagents write under `.coordination/` in the main checkout (the call centre's register,
  the manager's briefs in `.coordination/briefs/`, resume notes); the factory, manager, call-centre, usage and terse
  skills close the review's gaps: the master loop through the orchestrator, coders reaching the call centre through
  it, `CHANGELOG.md` as the one shared scope glob, merges committed only after a green gate, push only what the
  user named, "start nothing heavy" defined, warnings below the stop level only prompting a reading, the usage tool
  found from another project, and a `stopped` verdict (D-027) (`review/fix-orchestration`).
- The research and archaeology roles treat everything in their session context besides the brief as internal,
  never start an agent, strip internal details whoever sends them, and report merged work as "stopped" on a usage
  stop (`archaeologist`, `archaeologist-master`, `researcher`, `research-master` 1.1.0) (`review/fix-research`).
- **Removed**: the hook that refused `git push` in Claude sessions, and the git `pre-push` guard; re-run
  `just guards-install <project>` to remove the old `pre-push` hook. Agents still never push unless the user
  explicitly asks for that push in their own words (D-025) (`main`).
- The factory reads usage before every start and every 10 minutes while agents run; at 95% every running agent
  stops cleanly with a resume note and restarts after the reset (`usage`, `factory`, `manager`), and `git-flow`
  says a restructuring is done in a worktree and lands in one fast-forward (D-023, D-024) (`main`).
- `git-flow` now says a merge is committed only once its gate has been read green, and names the shortcut of
  scripting merge and commit together as a red flag (D-015) (`main`).
- The terse-message skill is now `luna-factory:terse`; **Breaking**: briefs naming `luna-factory:caveman` must
  name `luna-factory:terse` (D-014) (`main`).
- The factory's build roles are written: two planners with opposite stances (smallest change, most robust
  design), a mixer that compares them on one grid and freezes the contract and the split by side, coders who work
  test first and prove every claim with the recipes, breakers who turn every hole into a committed failing test,
  a reviewer who refuses incomplete work and signs off explicitly, and the git flow every agent follows (worktree
  and branch per task, commits, changelog line, merges one at a time, network share quirks) (`skills/factory-build`).
- The research roles of the factory are written: archaeologists answer what the project already has from local
  sources only, with evidence for every claim and no network; researchers answer what exists outside from the web,
  with generic queries that never leak the project and licences checked; their two masters split or overlap a
  question across several agents, then merge, rank and rate the findings and flag conflicts and gaps
  (`skills/factory-research`).
- `luna-factory` now runs the line: the `factory` skill guides the orchestrator (framing, fresh scoped agents,
  watching, one merge at a time, review until sign-off), `manager` turns an approved plan into briefs with a
  template and expertise picked per task, `call-centre` keeps the coordination register and hands out unique
  numbers and keys, `usage` gates every start on `just usage` and stops the line on a limit message, and
  `caveman` sets the terse style of messages between agents (`skills/factory-orchestration`).

### marketplace

- `luna-backend` and `luna-tooling` declare `luna-quality` as a dependency, and the choices the skill writers built
  in are recorded (D-016, D-017) (`main`).
- The expertise plugins `luna-frontend`, `luna-backend`, `luna-quality` and `luna-tooling` join the marketplace,
  and all 26 skills exist as skeletons whose names, descriptions and kinds are the contract the skill writers
  work against (`main`).
- The ToolBox becomes the `lunas-toolbox` Claude Code marketplace, licensed AGPL-3.0-only: a core plugin,
  `luna-factory`, whose hooks keep agents inside their worktree's scope and refuse any `git push` from a Claude
  session, and expertise plugins that cost no context until a brief names a skill (`just expertise <skill>`).
  Skills follow a shared template, checked by `just check-skills`; `CREDITS.md` is generated from the sources
  each skill names, and `just eval <skill>` runs a skill's rare evals by hand (D-006 to D-011) (`main`).

### tooling

- `usage/` can be published on its own: it carries its licence, a front-page README, its own changelog and git
  files, and names nothing of the ToolBox (D-026) (`main`).
- `just usage` says how to act on a stop: "stop running agents cleanly; resume after <reset time>", naming the
  reset of the window that stopped (D-023) (`main`).
- `just usage` now stops the line at 95% of either window (five-hour was 85%, seven-day was 90%), keeping 5% for
  running agents to stop cleanly; caution stays at 70% of the five-hour window (D-019) (`main`).
- **Removed**: the Docker lock (`just lock`, `tools/docker_lock.py`): Docker commands now run normally, and the
  skills no longer ask agents to take a lock; drop any `DOCKER_LOCK` setting you made for it (D-018) (`main`).
- The repository tests now also check new files before they are committed, so a writer's gate catches what
  the main branch would refuse (`main`).
- `just usage` now takes a fresh reading on demand from the Agent SDK's `/usage` command, at no token cost, cached
  for a minute; **Removed**: the status line writer and `just usage-install`, so drop any `usage_statusline.py`
  status line from your Claude Code settings; run `just setup` once to install the SDK (needs Node.js) (D-013)
  (`main`).
- `just usage` tells the factory whether it may start agents (go, caution, stop, weekly, unknown) from the plan
  usage a terminal meter's status line records, and `just usage-install` shows the status line setting to add,
  keeping the current one on screen (D-012) (`main`).
- Guards that enforce the checkable rules at no token cost, installed in any project with
  `just guards-install <project>`: commit messages must be Conventional Commits without AI attribution, staged
  files LF only with English comments, pushes refused (the user pushes with `git push --no-verify`), and
  `just changelog-check` in the gate fails a change without its changelog line. Heavy recipe scripts can take
  the Docker lock themselves with `docker_lock.locked()`. Behaviour evals become a hand-run last resort
  (D-004, D-005) (`main`).
- Recipes for every manual job (`just setup`, `test`, `lint`, `format`, `ci`), run by a Python shell so arguments
  reach the scripts intact on every OS (D-001, D-002), and the machine-wide Docker lock as a tested tool,
  `just lock <agent> <command...>`, whose path defaults to the user cache folder and is shared through
  `DOCKER_LOCK` (D-003) (`main`).

### rules

- Repositories on the network share turn git's automatic maintenance off (`maintenance.auto false`,
  `gc.auto 0`), and agents run it by hand after a large merge into the development branch or when git feels
  slow, never while another session works on the repository (`main`).
- The call centre's register moves to `.coordination/COORDINATION.md` (git-ignored by the repository) and heavy
  Docker runs go through `just lock`; no rule points into a machine-wide ignored folder any more (D-003) (`main`).
- Work delegated to another Claude session goes through the chat that delegated it: questions, decisions, plans
  and reports, so the user only talks to that master chat (`main`).
- Archaeologist and research masters join the agent factory: each delegates one question to several agents at
  once, overlapping or splitting the search as the question needs, then merges, ranks and rates their findings;
  archaeologists stay local, researchers stay on the web with a generic brief, so nothing internal leaks (`main`).
- Working rules taken from another project, with an empty repo-specific section, and an agent factory that replaces the
  agents and call-centre rules: a tree of fresh, scoped agents (orchestrator, reviewer, manager, call centre, two
  planners and a mixer, coders per side, breakers), caveman messages between agents, and a closed list of skills
  per role (`main`).

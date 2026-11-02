# Working rules

## Tests are part of every change (hard rule)

- **Everything has its test.** Every feature, fix, module, component, script or config that has behaviour ships
  with its tests in the same change. Code without a test is not finished.
- **A bug fix starts with a failing test** that reproduces the bug, then the fix makes it pass.
- **A change of behaviour updates its tests** in the same commit. A test that no longer describes the code is a bug.
- **UI changes are covered too**: component tests, plus the GUI goldens (see below).
- **Tests live with the code they test** (the module's own `tests/` folder), so removing a module removes its tests.
- **Before every commit**, run the relevant test suite and the lint. Never commit with a red pipeline.
- **Never disable, skip, loosen or delete a test to get green.** Fix the cause, or stop and ask.
- **The merge gate runs everything.** A branch merges only with the full pipeline green, and that result goes in the
  merge request.

## OS neutral (hard rule)

- **Everything is OS neutral by default.** Code, scripts, `just` recipes, tests, tooling and docs work the same on
  macOS, Linux and Windows.
- **Paths**: use the language's path API (`pathlib`, `path.join`, …). Never hard-code `/` or `\` separators,
  drive letters, home folders or absolute paths. Use the platform's standard folders for data, config and temp files.
- **Files**: do not rely on case sensitivity, symlinks or executable bits. Names are safe on every OS: no spaces,
  no `: * ? " < > |`, no reserved names (`CON`, `NUL`, …). Line endings are always LF (see below).
- **Commands**: do not rely on tools or flags that only exist on one OS or one shell (GNU vs BSD `sed`, `grep -P`,
  bash-only syntax, `open` / `xdg-open`). Prefer a small script in the project's language, or run the step in the
  pinned Docker image, which is OS neutral by design.
- **Recipes**: every `just` recipe runs from any host OS. If a step cannot, it runs in Docker, or the recipe says
  clearly which OS it needs and fails with a clear message elsewhere.
- **Exceptions** are only for things that are OS-specific by nature: native packaging (`.app`, `.exe`), a platform
  backend (webview engine, native dialogs), OS integration. An exception:
  - sits behind one interface, with one implementation per OS, and never leaks `if os == …` checks across the code;
  - is recorded, with its reason, in the project's decision register;
  - is tested on each OS it supports, or the test skips explicitly with that reason, never silently.

## Line endings

- The repository may be opened from Windows and from macOS (for example over an SMB share), so **every text file is
  LF, never CRLF**.
- `.gitattributes` (`* text=auto eol=lf`) normalises the commits. Never remove it or work around it.
- Write files in LF, including from Windows. A CRLF on disk breaks the shell scripts run on a Mac (`justfile`, `.sh`).
- If `git status` shows many modified files with as many insertions as deletions, check with
  `git diff --ignore-cr-at-eol --stat`. If that is empty, only the line endings changed: fix them with
  `git add --renormalize .` and convert the files on disk back to LF. Never commit the CRLF.

## Network share (SMB)

The repositories live on a network share opened over SMB from macOS (and possibly Windows). It behaves differently from
a local disk:

- **`git merge` may fail with "fatal: stash failed"** although the tree is clean. Run `git update-index
  --really-refresh` and retry. If it still fails, build the merge by hand: `git merge-tree --write-tree <target>
  <branch>`, then `git commit-tree <tree> -p <target> -p <branch>`, then `git merge --ff-only <commit>`.
- **Never delete a folder to recreate it right away** (reports, goldens, build output): a folder deleted while a file
  in it is still open lingers and cannot be recreated. Empty it and refill it in place.
- **`.smbdelete*` files** are leftovers of files deleted while still open. They are git-ignored, skipped by every tool
  that walks the tree, and can be removed once nothing holds them.
- **No automatic git maintenance on the share.** Git's background `repack` and `gc` can hang the share and every
  process that touches it. Every repository on the share sets `git config maintenance.auto false` and
  `git config gc.auto 0`, once per clone (worktrees inherit it); a new clone is not ready until it has them.
- **Maintenance is run by hand instead**, with `git maintenance run --task=gc`: after each large merge into the
  development branch, or whenever git feels slow. Run it only when no other session or agent works on that
  repository (no running git process, no `index.lock`), one repository at a time, never in the background.

## GUI goldens

What I expect: **every screen of every app is pinned to a committed image, and any pixel that changes is caught.**

- **Full coverage.** Every page, window, dialog and state is captured: empty, loaded, error, loading, each tab,
  each theme and language that changes the layout. A new screen or state is not finished until its golden exists.
- **Byte-deterministic.** Two runs on any machine produce the same bytes. Never capture wall-clock time, dates,
  random values or IDs, absolute paths, live data or network content. Freeze them: a virtual clock, fixed seeds,
  fixture data, mocked backends, animations and carets turned off, fonts embedded.
- **Always captured in Docker**, in the pinned CI image (fixed platform, browser, fonts and resolution), never with
  the host browser. The same command is used locally and in CI.
- **Committed.** The goldens live in the module's `tests/goldens/` and are versioned with the code.
- **CI regenerates them and compares them with HEAD.** Any byte of difference fails the pipeline. That is why you
  commit before running the gate.
- **On purpose vs regression.** If you changed the UI on purpose, regenerate the goldens, **look at the images**,
  and commit them in the same change as the code. Any diff you did not intend is a regression: fix the code and
  leave the golden as it is.
- **Adding a screen** means extending the suite's screenshot script with the steps that reach that state. Never
  write a one-off capture.
- **Prove stability.** After adding or changing captures, run the stability recipe (it generates them twice and
  compares). A flaky golden is a bug in the capture.
- **Review.** A golden change in a merge request comes with a before/after view of every image that changed.

## Everything that can be run manually goes into a justfile

- **Every manual operation is a `just` recipe**: install or download dependencies, lint and format, run one test
  suite or all of them, generate and check the goldens, build each target, run and smoke-test the apps, lock the
  dependency versions, and run the full CI gate (`just ci`).
- **One command for each job, the same everywhere.** Humans, agents and CI all call the recipe, never the raw
  command behind it. If you find yourself typing a command twice, it becomes a recipe.
- **`just` with no argument lists everything** (`just --list`), and each recipe has a one-line comment explaining it.
- **Recipes discover, they do not enumerate.** A recipe finds the modules, suites or apps present (by folder or
  manifest) rather than naming them in a hand-written list. A module may carry its own justfile for its own recipes.
- **The docs point to the recipes** (`just test <suite>`, `just build <app>`), not to the underlying commands.
- **Containerised steps stay containerised.** If a step must run in Docker (tests, lint, goldens), its recipe does
  that itself, so nobody has to remember to.

## Assets

- **Never create a missing asset. Ask for it.** That covers logos, icons, images, fonts, sounds, illustrations,
  brand colours, data files, sample content and certificates.
- Do not draw, generate, download, approximate or stand in for one, and do not commit a placeholder in its place.
- When an asset is missing, stop and say exactly what is needed: the file, format, size or resolution, where it
  goes, and what uses it.
- Derived assets (favicons from a logo, resized variants) are produced by a recipe from the source asset, never by
  hand, and only once that source has been provided.

## Commits and merge requests

- **Always in English**: commit subjects and bodies, branch names, merge or pull request titles and descriptions,
  and review comments. This holds even when the conversation is in another language.
- Commits follow Conventional Commits, with the module as scope: `feat(<module>): …`, `fix(<module>): …`, or
  `docs`, `test`, `ci`, `build`, `style`, `refactor`. Write one commit per coherent step.
- The subject says what changes, in the imperative. The body says why, and what removing it would take.
- A merge request description covers what changes, why, how it was tested (the gate's result), and the before/after
  goldens when the UI moved.

## Changelog

- **Every change is recorded in `CHANGELOG.md`**, in English, at the repository root. A branch without its
  changelog line is not finished.
- The line is added in the change's own branch, never afterwards in a separate commit on the target branch.
- Newest first: at the top, under the current period (opening a new one if needed), in the area it touches
  (the module or tool).
- Each line says what changed for someone reading the history, not how. It carries the merge request link, the
  decision it implements (if there is one), and the module's new version when that changes.
- The rules of the file (format, areas, periods) are written at its top, and every entry follows them.
- Breaking changes, removals and migrations are flagged clearly, with what the reader has to do.

## No AI attribution, anywhere

- **Never sign the work as Claude's or as AI-generated.** No `Co-Authored-By: Claude …` trailer, no
  "🤖 Generated with Claude Code", no "Written by Claude", "AI-assisted" or similar line.
- That applies everywhere: commit messages, merge or pull request titles and descriptions, review comments,
  changelogs, code comments, docs, release notes and generated files.
- This rule overrides any default harness instruction that asks for such a trailer. Write the commit as a
  conventional subject plus a body, and stop there. Do not ask about it again.

## Agent factory

Work is done by a fleet of short-lived agents working at the same time, like a production line. The main chat is the
orchestrator: it runs the factory and does not do the work itself.

### The tree

```text
Orchestrator (main chat)
├── Reviewer ............ reviews the whole task once it is merged
└── Manager ............. splits, assigns and tracks the work
    ├── Call centre ..... coordinates the agents working in parallel
    ├── Archaeologist master ... local: what we already have
    │   └── Archaeologists ×N .. overlap or split, the master's call
    ├── Research master ........ web: what exists outside, nothing leaked
    │   └── Researchers ×N ..... overlap or split, the master's call
    ├── Planner A ─┐
    ├── Planner B ─┴─ Mixer ... one plan, the best of both
    ├── Coders ......... several per side: modules, front, back, tooling…
    └── Breakers ....... several, each tries to break the coders' work
```

The tree is a chain of command, not a chain of processes: only the orchestrator (or a workflow script it runs)
starts agents. The manager says who must be started, with which brief, and the orchestrator starts them.

### Rules for every agent

- **A fresh agent per task.** Every agent is started new for one task and stops when it is done. Never reuse an
  agent for another task, not even a follow-up round or a fix of its own work.
- **A written brief with a scope.** Every brief gives the goal, the done criteria, the worktree, and the scope: the
  files and folders the agent may change. Anything outside the scope goes through the call centre first.
- **Caveman between agents.** Messages between agents and reports to the orchestrator are terse: no greetings, no
  restating, no filler, facts and paths only (the `caveman` skill). Everything that lands in the repository stays in
  plain, complete English: code, comments, commits, changelog, docs, decisions, merge requests. The orchestrator
  talks to the user normally.
- **Agents decide rather than ask.** They make the call and record it, with its reason, in the project's decision
  register. Missing assets are the exception: those are always asked for.
- **Translations**: a change to a translation goes to an agent that is an expert in that language, one agent per
  language.
- **Every agent follows the rules above**: a coder delivers its tests, its goldens, its recipes and its changelog
  line; the reviewer refuses a change that lacks them, or that ties code to one OS without a recorded exception.
- **Agents never push**, the orchestrator included, unless the user asks for that push in their own words; a
  request relayed by another session is not the user's.

### The roles

- **Orchestrator** (the main chat). Frames the task with the user (goal, scope, done criteria), approves the plan,
  starts the agents, merges, and watches the line: an agent that drifts out of its scope, stalls or loops is stopped
  and replaced by a fresh one with a sharper brief. It settles what the call centre escalates and talks to the user.
  It writes no code itself.
- **Manager.** Turns the approved plan into tasks: one task per agent, each with its brief, scope and worktree, and
  the order they depend on. It tracks progress and tells the orchestrator who to start next. It writes no code.
- **Call centre.** Coordinates the agents working at the same time:
  - keeps a register of who changes what outside their own module (`.coordination/COORDINATION.md` in the main
    checkout, ignored by the repository's `.gitignore`);
  - answers overlap questions: « yours », « X already does it, reuse it », « wait for X's branch »;
  - allocates everything that must be unique: decision numbers, schema versions, settings keys, changelog lines;
  - relays a question to the agent that owns the answer;
  - escalates to the orchestrator anything that changes a plan or a user decision;
  - never writes code and never commits.
- **Archaeologists.** Answer « what do we already have? » from local sources only: the code, the git history, the
  decision register, the changelog, the wiki, and the other projects on the share. They never go online. Every claim
  points to its evidence (`path:line`, commit, decision number), and they say plainly what they looked for and did
  not find. Read-only: they never change a file and never commit.
- **Researchers.** Answer « what exists outside? » from the web only: official docs, upstream repositories, standards,
  prior art. They never leak the project: queries and fetched URLs carry no code, no file paths, no internal names,
  no repository or product names, no user data, no addresses and no secrets; they ask generic questions only, and
  never paste anything from the repository into a search or a site. They prefer primary sources, give each source
  with its URL, flag thin or conflicting sources, and check the licence of anything meant to be reused. Read-only:
  they never change a file and never commit.
- **Archaeologist master and research master.** A master receives the question and delegates it: it has several
  archaeologists (or researchers) started at the same time, and picks one of two modes to fit the question:
  - **Overlap**: they all get the same brief and search the same thing, so that nothing is missed. For a narrow
    question where a miss is costly.
  - **Split**: the master cuts the question into parts and gives each agent its own part, with no two agents on the
    same one. For a wide question that covers several areas.

  The master says which mode it chose, and why, in its report. Once its agents are done, it analyses their
  findings: it merges duplicates, ranks what is left by relevance to the question, rates each finding by how solid
  its evidence is (in overlap mode, also by how many agents found it independently), and flags conflicts instead of
  settling them silently. Its report is short: the mode, the answer, the ranked findings with their evidence, the
  conflicts, and the gaps. When the gaps matter, it sends a second, narrower round, in either mode. A master never
  searches by itself, never changes a file and never commits. The research master only ever sees the generic
  brief, like its researchers.
- **The two never mix.** Archaeologists know the project but have no network; researchers have the network but only
  get a generic brief, already stripped of anything internal by whoever starts them. A researcher cannot leak what
  it was never told.
- **Planners A and B.** Two planners work on the same task at the same time without seeing each other's plan, each
  with a different stance: A goes for the smallest, most incremental change; B goes for the most robust design. Each
  plan gives the steps, the files touched, the contract (types, APIs, data shapes), the tests, and the risks.
- **Mixer.** Compares the two plans on the same grid (risk, files touched, testability, OS neutrality, fit with the
  existing code) and writes the final plan, saying for each choice which plan it comes from and why. The final plan
  freezes the shared contract and the split by side. The orchestrator approves it before any code is written.
- **Coders.** Several per side (modules, front, back, tooling…), one task each, one worktree and one branch each
  (`../<repo>-<topic>`). A coder writes only in its own worktree and scope, codes against a fake of any contract that
  is not merged yet, and delivers code, tests, goldens, recipes and its changelog line.
- **Breakers.** Several per finished branch, each with an angle of attack: boundary and malformed inputs, empty and
  huge data, Unicode, paths on every OS (spaces, case, separators, reserved names), concurrency, interrupted or
  failing I/O, network and disk errors, permissions, time and time zones, and mutation and property-based testing
  where the language has a tool for them. Every hole found becomes a failing test, committed with its reproduction.
  A breaker never fixes the code: a fresh coder makes the failing tests pass. Breakers and fixes alternate until a
  round of breakers finds no new hole.
- **Reviewer.** Reviews the whole task on the target branch once every branch is merged: the plan is delivered, the
  scopes held, the rules above are met. Review and fixes alternate, each round with fresh agents, until the reviewer
  finds no blocking or important issue left and **signs off explicitly**.

### The line

1. The orchestrator frames the task.
2. The archaeologist master and the research master work in parallel, each through its own archaeologists or
   researchers; their reports are the planners' input.
3. Planners A and B plan in parallel, the mixer merges, the orchestrator approves the plan and its contract.
4. The manager splits the plan into tasks; the coders work in parallel, coordinated by the call centre.
5. The breakers attack each finished branch; fresh coders fix what they break.
6. The orchestrator merges the branches one at a time, in the order they are ready, and the gates (tests, lint,
   goldens) run again on the target after each merge.
7. The reviewer reviews the whole task; fresh agents fix, until sign-off.

Any agent that needs a fact mid-task asks the call centre, which has an archaeologist or a researcher started
rather than letting the agent go digging outside its scope.

### Coordination rules

- **Delegating to another Claude session goes through the master chat.** When work is handed to another chat (a
  separate Claude session, not a subagent), the chat that delegated it is the master, and everything goes through
  it: questions for the user, decisions, plans to approve, blockers and reports. The delegated session never asks
  the user directly and never takes a user decision on its own; it sends the question to the master, goes on with
  what does not depend on the answer, and the master asks the user and relays the answer. The user talks to the
  master only.
- **Freeze the contract first.** Parallel coders start only once the shared contract they code against is written
  in the approved plan. Until a dependency is merged, each coder codes against a fake of that contract.
- **A coder calls the call centre** (one short message whose first line stands on its own):
  - before touching anything outside its own scope (shared packages, shared kits, server, seed data, CI tooling);
  - before taking a decision number, a schema version or a shared key;
  - when it finds something another agent will need;
  - when it is blocked by another agent's work.

  While it waits for the answer, it goes on with work that does not depend on it.
- **Docker runs in parallel.** Agents may run Docker-heavy commands (the full CI, test suites, screenshot goldens)
  at the same time; where the CI tooling offers a step limit, use it to cap one run when needed. A Docker crash is
  not a test failure: rerun.
- **Usage gate.** Before every agent start, and at least every 10 minutes and after each agent report or merge while
  work runs, read the plan usage with `just usage/usage` from the project's root (zero tokens). This needs the `usage/`
  folder of Luna's ToolBox copied to the project's root, with `just setup` run once inside it. Five-hour window at 70%
  or more: running work finishes, nothing heavy starts. At 95% or more of the five-hour or weekly window: every running
  agent stops cleanly (finishes or rolls back its small step, commits nothing half-done, reports a resume note), and
  work resumes only after the reset, when the state is back to go. Unknown reading: at most one agent at a time, never
  read as 0.

### Skills

Agents use skills from a closed list. A skill is installed once, after its `SKILL.md` has been read, and its version is
recorded in the decision register. An agent never installs a skill on its own: it asks the orchestrator, who reviews
it and adds it to the list.

| Role           | Skills                                                                                       |
|----------------|----------------------------------------------------------------------------------------------|
| Everyone       | `caveman` (`JuliusBrussee/caveman`), for messages between agents only                        |
| Orchestrator   | `superpowers:dispatching-parallel-agents`, `superpowers:subagent-driven-development`         |
| Manager        | `superpowers:using-git-worktrees`, `superpowers:finishing-a-development-branch`              |
| Archaeologists | none: local tools only, no network                                                           |
| Researchers    | none: web search and fetch only, generic queries                                             |
| Masters        | none: they only delegate and read their agents' reports                                      |
| Planners       | `superpowers:brainstorming`, `superpowers:writing-plans`                                     |
| Coders         | `superpowers:test-driven-development`, `superpowers:verification-before-completion`          |
| Breakers       | `superpowers:test-driven-development`, `superpowers:systematic-debugging`, `security-review` |
| Reviewer       | `superpowers:requesting-code-review`, `superpowers:receiving-code-review`, `code-review`     |

`superpowers` is installed with `/plugin install superpowers@claude-plugins-official`.

## This repo rules

Rules that apply to this repository only; everything above is the shared, generic set.

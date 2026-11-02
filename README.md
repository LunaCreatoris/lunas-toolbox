# Luna's ToolBox

Two folders for working with Claude Code agents.

| Folder | What it is |
|---|---|
| [usage/](usage/README.md) | The usage gate: reads the plan usage of your own claude.ai login through the Agent SDK at no token cost, and says whether agents may start or keep running |
| [claude/](claude/CLAUDE.md) | The generic working rules: tests, OS neutrality, goldens, recipes, commits, changelog, and an agent factory built on third-party skills |

## How to use them

- **Usage gate**: copy the `usage/` folder into a project, then run `just setup` and `just usage` inside it.
  Personal use only: it reads your own usage, for yourself, see
  [usage/README.md](usage/README.md#how-it-reads-the-usage).
- **Working rules**: copy `claude/CLAUDE.md` to a project's root.

History: [CHANGELOG.md](CHANGELOG.md).

## Licence

GNU Affero General Public License v3.0 only (`AGPL-3.0-only`), see [LICENSE](LICENSE).

// Print the plan usage of the user's own claude.ai login as one JSON line, read through
// the Agent SDK's /usage command (D-013). /usage is a local command: no model request is
// made, and no token is spent. The SDK uses the login Claude Code already has; this script
// never reads, copies or stores a credential.
//
// Usage: node read_usage.mjs <working folder>
// Output: {"report": <usage_report or null>, "cost": <total_cost_usd>} or {"error": "..."}.

import { pathToFileURL } from "node:url";

// The only options the reading needs. persistSession: false keeps the SDK from writing a
// session transcript for every reading; no settings, tools or turns beyond the command.
export function usageOptions(cwd) {
  return {
    model: "claude-haiku-5-5",
    maxTurns: 1,
    settingSources: [],
    allowedTools: [],
    persistSession: false,
    cwd,
  };
}

export async function readUsage(query, cwd) {
  let report = null;
  let cost = null;
  for await (const message of query({ prompt: "/usage", options: usageOptions(cwd) })) {
    if (message.type === "assistant" && message.usage_report) {
      report = message.usage_report;
    }
    if (message.type === "result") {
      cost = message.total_cost_usd ?? null;
    }
  }
  return { report, cost };
}

async function main() {
  try {
    const { query } = await import("@anthropic-ai/claude-agent-sdk");
    const result = await readUsage(query, process.argv[2] ?? process.cwd());
    process.stdout.write(`${JSON.stringify(result)}\n`);
    return 0;
  } catch (error) {
    process.stdout.write(`${JSON.stringify({ error: String(error?.message ?? error) })}\n`);
    return 1;
  }
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? "").href) {
  process.exitCode = await main();
}

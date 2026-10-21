// The usage reader: the options it passes to the SDK and how it picks the report.
// Runs with `node --test`, through `just test`, against a fake SDK query.

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

import { readUsage, usageOptions } from "../sdk/read_usage.mjs";

function fakeQuery(messages, seen) {
  return (call) => {
    seen.push(call);
    return (async function* stream() {
      yield* messages;
    })();
  };
}

test("a reading never leaves a session transcript behind", () => {
  assert.equal(usageOptions("/tmp/x").persistSession, false);
});

test("a reading loads no settings, no tools and takes one turn at most", () => {
  const options = usageOptions("/tmp/x");
  assert.deepEqual(options.settingSources, []);
  assert.deepEqual(options.allowedTools, []);
  assert.equal(options.maxTurns, 1);
  assert.equal(options.cwd, "/tmp/x");
});

test("the /usage command is sent with those options", async () => {
  const seen = [];
  await readUsage(fakeQuery([], seen), "/tmp/x");
  assert.equal(seen[0].prompt, "/usage");
  assert.deepEqual(seen[0].options, usageOptions("/tmp/x"));
});

test("the report and the cost are taken from the stream", async () => {
  const report = { rate_limits: { limits: [] } };
  const messages = [
    { type: "system", subtype: "init" },
    { type: "assistant", message: { model: "<synthetic>" }, usage_report: report },
    { type: "result", subtype: "success", total_cost_usd: 0 },
  ];
  assert.deepEqual(await readUsage(fakeQuery(messages, []), "/tmp/x"), { report, cost: 0 });
});

test("no report in the stream gives null, never an empty reading", async () => {
  const messages = [{ type: "assistant", message: {} }, { type: "result", total_cost_usd: 0 }];
  assert.deepEqual(await readUsage(fakeQuery(messages, []), "/tmp/x"), { report: null, cost: 0 });
});

test("the SDK version is pinned exactly", () => {
  const manifest = JSON.parse(readFileSync(new URL("../sdk/package.json", import.meta.url), "utf8"));
  assert.match(manifest.dependencies["@anthropic-ai/claude-agent-sdk"], /^\d+\.\d+\.\d+$/);
});

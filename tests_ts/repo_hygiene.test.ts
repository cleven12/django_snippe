import { describe, expect, test } from "bun:test";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join, resolve } from "node:path";

const REPO_ROOT = resolve(import.meta.dir, "..");

const EMOJI_REGEX =
  /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{2B50}\u{2934}\u{2935}\u{2192}\u{2014}]/u;

function walkFiles(dir: string, results: string[] = []): string[] {
  for (const entry of readdirSync(dir)) {
    if (
      [
        ".git",
        ".venv",
        ".venv_check",
        "node_modules",
        "__pycache__",
        "dist",
        "build",
      ].includes(entry)
    ) {
      continue;
    }
    const full = join(dir, entry);
    const st = statSync(full);
    if (st.isDirectory()) {
      walkFiles(full, results);
    } else if (/\.(py|md|toml|yml|yaml|json|ts)$/.test(entry)) {
      results.push(full);
    }
  }
  return results;
}

describe("Repository Hygiene & Zero AI Artifact Checks", () => {

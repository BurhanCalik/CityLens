#!/usr/bin/env node
// CityLens — Cursor SDK automation (BONUS: AI Adaptasyonu).
//
// Reads detections.json and uses the Cursor SDK (@cursor/sdk) to generate a
// Turkish, municipality-facing triage report at docs/REPORT.md.
//
// Usage:
//   export CURSOR_API_KEY=cursor_...        (https://cursor.com/dashboard/integrations)
//   node tools/cursor/summarize_detections.mjs

import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { Agent, CursorAgentError } from "@cursor/sdk";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..", "..");

const CANDIDATES = [
  resolve(ROOT, "data/processed/detections.json"),
  resolve(ROOT, "backend/internal/infrastructure/detection/detections.json"),
  resolve(ROOT, "web/public/detections.json"),
];

function loadDetections() {
  for (const path of CANDIDATES) {
    if (existsSync(path)) {
      return { path, data: JSON.parse(readFileSync(path, "utf8")) };
    }
  }
  throw new Error("detections.json not found in any known location");
}

function summarize(data) {
  const stats = { total: data.length, bySeverity: {}, byLabel: {}, avgScore: 0 };
  let scoreSum = 0;
  for (const d of data) {
    const sev = d.severity ?? "info";
    stats.bySeverity[sev] = (stats.bySeverity[sev] ?? 0) + 1;
    stats.byLabel[d.label] = (stats.byLabel[d.label] ?? 0) + 1;
    scoreSum += d.score ?? 0;
  }
  stats.avgScore = data.length ? Number((scoreSum / data.length).toFixed(3)) : 0;
  return stats;
}

async function main() {
  const apiKey = process.env.CURSOR_API_KEY;
  if (!apiKey) {
    console.error("CURSOR_API_KEY is not set. See https://cursor.com/dashboard/integrations");
    process.exit(1);
  }

  const { path, data } = loadDetections();
  const stats = summarize(data);
  console.log(`Loaded ${stats.total} detection(s) from ${path}`);

  const prompt = [
    "Aşağıdaki CityLens kentsel denetim verisinden Türkçe, yöneticiye yönelik",
    "kısa bir özet rapor (markdown) üret. Belediye saha ekipleri için",
    "önceliklendirme öner. Abartma; yalnızca veriye dayan.",
    "",
    "VERİ (özet JSON):",
    JSON.stringify(stats, null, 2),
  ].join("\n");

  try {
    // One-shot pattern: disposes itself, ideal for a CI/automation step.
    const result = await Agent.prompt(prompt, {
      apiKey,
      model: { id: "composer-2.5" },
      local: { cwd: ROOT },
    });

    if (result.status === "error") {
      // Run executed but failed mid-flight.
      console.error("run failed:", result.id);
      process.exit(2);
    }

    const out = resolve(ROOT, "docs/REPORT.md");
    writeFileSync(out, String(result.result ?? ""), "utf8");
    console.log("Report written ->", out);
  } catch (err) {
    if (err instanceof CursorAgentError) {
      // Run never started (auth/config/network).
      console.error("startup failed:", err.message, "retryable=", err.isRetryable);
      process.exit(1);
    }
    throw err;
  }
}

main();

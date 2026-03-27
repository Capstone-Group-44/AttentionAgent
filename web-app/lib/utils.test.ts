import { describe, test, expect } from "vitest";
import { formatDuration, focusScoreToPercent } from "./utils";
import { parseDurationToUnit } from "./utils";

describe("utils", () => {
  test("formatDuration works", () => {
    expect(formatDuration(65)).toBe("1m 5s");
  });

  test("focusScoreToPercent works", () => {
    expect(focusScoreToPercent(0.8)).toBe(80);
  });
  test("formatDuration handles edge cases", () => {
    expect(formatDuration(0)).toBe("0s");
    expect(formatDuration(3600)).toBe("1h 0m");
  });
  test("focusScoreToPercent handles NaN", () => {
    expect(focusScoreToPercent(NaN)).toBe(0);
  });
  test("parseDurationToUnit parses hours correctly", () => {
    const result = parseDurationToUnit("1h", "minutes");

    expect(result?.value).toBe(60);
  });
});

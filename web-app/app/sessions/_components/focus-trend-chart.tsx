"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { Timestamp } from "firebase/firestore";
import type { FocusSample } from "@/lib/api/focus-samples";

type Props = {
  samples: FocusSample[];
  sessionStart: Timestamp;
};

type ChartPoint = {
  time: number; // seconds since start
  focus: number; // 0-100
};

function formatTime(sec: number) {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

function bucketToSeconds(samples: FocusSample[], startMs: number, bucketMs = 1000): ChartPoint[] {
  const buckets = new Map<number, { sum: number; n: number }>();

  for (const s of samples) {
    const ms = s.timestamp.toDate().getTime() - startMs;
    const key = Math.floor(ms / bucketMs);

    const cur = buckets.get(key) ?? { sum: 0, n: 0 };
    cur.sum += (s.focusScore ?? 0);
    cur.n += 1;
    buckets.set(key, cur);
  }

  return Array.from(buckets.entries())
    .sort(([a], [b]) => a - b)
    .map(([key, v]) => ({
      time: (key * bucketMs) / 1000,
      focus: Math.round(((v.sum / v.n) * 100) * 10) / 10, // 1 decimal
    }));
}

function smoothData(data: ChartPoint[], windowSize = 5): ChartPoint[] {
  return data.map((_, i) => {
    const start = Math.max(0, i - windowSize);
    const end = Math.min(data.length, i + windowSize);

    const slice = data.slice(start, end);
    const avg =
      slice.reduce((sum, p) => sum + p.focus, 0) / slice.length;

    return {
      ...data[i],
      focus: Math.round(avg * 10) / 10,
    };
  });

  
}

function smoothRawSamples(samples: FocusSample[], windowSize = 10): FocusSample[] {
  return samples.map((_, i) => {
    const start = Math.max(0, i - windowSize);
    const end = Math.min(samples.length, i + windowSize);

    const slice = samples.slice(start, end).filter(s => s.focusScore != null);

    const avg =
      slice.reduce((sum, s) => sum + (s.focusScore ?? 0), 0) / slice.length;

    return {
      ...samples[i],
      focusScore: avg,
    };
  });
}

export function FocusTrendChart({ samples, sessionStart }: Props) {
  const startMs = sessionStart.toDate().getTime();

  // Convert raw samples into chart points
  const durationSec =
  (samples[samples.length - 1]?.timestamp.toDate().getTime() - startMs) / 1000;

const bucketMs =
  durationSec > 600 ? 5000 :   // >10 min → 5s buckets
  durationSec > 180 ? 3000 :   // >3 min → 3s buckets
  1000;

const cleanedSamples = smoothRawSamples(samples, durationSec > 600 ? 15 : 8);

const data = bucketToSeconds(cleanedSamples, startMs, bucketMs);
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 12, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false}/>

          <XAxis
            dataKey="time"
            tickFormatter={(v) => formatTime(Number(v))}
            tickLine={false}
            axisLine={false}
          />

          <YAxis domain={[0, 100]}
            ticks={[25, 50, 75, 100]}
            tickLine={false}
            axisLine={false}
          />

          <Tooltip
            formatter={(value) => [`${value}/100`, "Focus"]}
            labelFormatter={(label) =>
              `Time: ${formatTime(Number(label))}`
            }
          />

          <Line
            type="monotone"
            dataKey="focus"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import type { Run } from "../types";

interface Props {
  runs: Run[];
}

export default function CoverageChart({ runs }: Props) {
  const data = runs
    .filter((r) => r.coverage_after != null)
    .reverse()
    .map((r, i) => ({
      run: i + 1,
      coverage: r.coverage_after,
    }));

  if (data.length === 0) {
    return <p className="text-gray-400 text-sm">No coverage data yet.</p>;
  }

  return (
    <div className="bg-white p-4 rounded-lg border">
      <h3 className="text-sm font-medium text-gray-500 mb-4">Coverage Trend</h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="run" label={{ value: "Run #", position: "bottom" }} />
          <YAxis domain={[0, 100]} label={{ value: "%", angle: -90, position: "insideLeft" }} />
          <Tooltip />
          <Line type="monotone" dataKey="coverage" stroke="#2563eb" strokeWidth={2} dot />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

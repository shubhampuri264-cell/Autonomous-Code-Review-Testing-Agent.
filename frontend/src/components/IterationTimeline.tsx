import { useEffect, useState } from "react";
import type { Correction } from "../types";

interface Props {
  runId: string;
}

export default function IterationTimeline({ runId: _runId }: Props) {
  const [corrections, setCorrections] = useState<Correction[]>([]);

  useEffect(() => {
    // TODO: fetch corrections for this run
    setCorrections([]);
  }, [_runId]);

  if (corrections.length === 0) {
    return null;
  }

  return (
    <div className="mt-8">
      <h2 className="text-xl font-semibold mb-4">Self-Correction Timeline</h2>
      <div className="space-y-4">
        {corrections.map((c) => (
          <div key={c.id} className="flex gap-4 p-4 border rounded-lg">
            <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-blue-100 text-blue-700 text-sm font-bold">
              {c.iteration}
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium">{c.failure_summary}</p>
              <p className="text-sm text-gray-500 mt-1">{c.patch_applied}</p>
              <span
                className={`mt-2 inline-block text-xs px-2 py-0.5 rounded-full ${
                  c.result === "resolved"
                    ? "bg-green-100 text-green-700"
                    : c.result === "partial"
                    ? "bg-yellow-100 text-yellow-700"
                    : "bg-red-100 text-red-700"
                }`}
              >
                {c.result}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

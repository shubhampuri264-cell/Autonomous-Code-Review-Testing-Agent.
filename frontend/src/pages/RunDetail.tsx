import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/client";
import RunStatusBadge from "../components/RunStatusBadge";
import TestFileViewer from "../components/TestFileViewer";
import IterationTimeline from "../components/IterationTimeline";
import usePolling from "../hooks/usePolling";
import type { Run } from "../types";

export default function RunDetail() {
  const { id } = useParams<{ id: string }>();
  const [run, setRun] = useState<Run | null>(null);

  const fetchRun = () => {
    api.get(`/runs/${id}`).then((res) => setRun(res.data));
  };

  // Poll while pending/running
  usePolling(fetchRun, 3000, run?.status === "pending" || run?.status === "running");

  useEffect(() => {
    fetchRun();
  }, [id]);

  if (!run) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-6xl mx-auto p-8">
      <div className="flex items-center gap-4 mb-6">
        <h1 className="text-2xl font-bold">Run Details</h1>
        <RunStatusBadge status={run.status} />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Stat label="Coverage" value={run.coverage_after != null ? `${run.coverage_after}%` : "—"} />
        <Stat label="Iterations" value={String(run.iterations)} />
        <Stat label="Trigger" value={run.trigger} />
        <Stat label="Started" value={run.started_at} />
      </div>

      {run.pr_url && (
        <a
          href={run.pr_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block mb-6 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          View Pull Request
        </a>
      )}

      {run.error_message && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <p className="font-medium">Error</p>
          <pre className="mt-1 text-sm whitespace-pre-wrap">{run.error_message}</pre>
        </div>
      )}

      <IterationTimeline runId={run.id} />
      <TestFileViewer runId={run.id} />
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="p-4 bg-white rounded-lg border">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-lg font-semibold">{value}</p>
    </div>
  );
}

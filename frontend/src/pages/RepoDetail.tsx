import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/client";
import RunStatusBadge from "../components/RunStatusBadge";
import CoverageChart from "../components/CoverageChart";
import type { Repository, Run } from "../types";

export default function RepoDetail() {
  const { id } = useParams<{ id: string }>();
  const [repo, setRepo] = useState<Repository | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);

  useEffect(() => {
    api.get(`/repositories`).then((res) => {
      const found = res.data.find((r: Repository) => r.id === id);
      setRepo(found || null);
    });
    api.get(`/runs?repo_id=${id}`).then((res) => setRuns(res.data));
  }, [id]);

  const triggerRun = () => {
    api.post("/runs/trigger", { repository_id: id }).then((res) => {
      setRuns((prev) => [res.data, ...prev]);
    });
  };

  if (!repo) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-6xl mx-auto p-8">
      <h1 className="text-2xl font-bold mb-2">{repo.github_url}</h1>
      <p className="text-gray-500 mb-6">
        Threshold: {repo.coverage_threshold}% | Branch: {repo.default_branch}
      </p>

      <button
        onClick={triggerRun}
        className="mb-8 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
      >
        Run Agent
      </button>

      <CoverageChart runs={runs} />

      <h2 className="text-xl font-semibold mt-8 mb-4">Run History</h2>
      <div className="space-y-3">
        {runs.map((run) => (
          <div
            key={run.id}
            className="flex items-center justify-between p-4 bg-white rounded-lg border"
          >
            <div>
              <RunStatusBadge status={run.status} />
              <span className="ml-3 text-sm text-gray-500">
                {run.started_at}
              </span>
            </div>
            <div className="text-sm">
              {run.coverage_after != null && (
                <span className="font-medium">{run.coverage_after}%</span>
              )}
              {run.iterations > 0 && (
                <span className="ml-3 text-gray-400">
                  {run.iterations} iterations
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

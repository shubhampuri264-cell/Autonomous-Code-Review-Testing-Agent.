import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import RepoCard from "../components/RepoCard";
import type { Repository } from "../types";

export default function Dashboard() {
  const [repos, setRepos] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/repositories").then((res) => {
      setRepos(res.data);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-6xl mx-auto p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Repositories</h1>
        <Link
          to="/connect"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Connect Repository
        </Link>
      </div>

      {repos.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <p className="text-lg">No repositories connected yet.</p>
          <p className="mt-2">Connect your first GitHub repo to get started.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {repos.map((repo) => (
            <RepoCard key={repo.id} repo={repo} />
          ))}
        </div>
      )}
    </div>
  );
}

import { Link } from "react-router-dom";
import type { Repository } from "../types";

interface Props {
  repo: Repository;
}

export default function RepoCard({ repo }: Props) {
  const repoName = repo.github_url.split("/").slice(-2).join("/");

  return (
    <Link
      to={`/repos/${repo.id}`}
      className="block p-6 bg-white rounded-lg border hover:border-blue-400 transition"
    >
      <h3 className="text-lg font-semibold text-gray-900">{repoName}</h3>
      <div className="mt-2 flex gap-4 text-sm text-gray-500">
        <span>Threshold: {repo.coverage_threshold}%</span>
        <span>Branch: {repo.default_branch}</span>
      </div>
      {repo.languages.length > 0 && (
        <div className="mt-3 flex gap-2">
          {repo.languages.map((lang) => (
            <span
              key={lang}
              className="px-2 py-1 text-xs bg-gray-100 rounded-full text-gray-600"
            >
              {lang}
            </span>
          ))}
        </div>
      )}
    </Link>
  );
}

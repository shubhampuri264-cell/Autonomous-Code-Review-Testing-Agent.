import { useEffect, useState } from "react";
import api from "../api/client";
import type { TestFile } from "../types";

interface Props {
  runId: string;
}

export default function TestFileViewer({ runId }: Props) {
  const [files, setFiles] = useState<TestFile[]>([]);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    // TODO: add endpoint to fetch test files by run_id
    api.get(`/runs/${runId}`).then(() => {
      // placeholder
    });
  }, [runId]);

  return (
    <div className="mt-8">
      <h2 className="text-xl font-semibold mb-4">Generated Test Files</h2>
      {files.length === 0 ? (
        <p className="text-gray-400 text-sm">No test files available.</p>
      ) : (
        <div className="space-y-2">
          {files.map((f) => (
            <div key={f.id} className="border rounded-lg">
              <button
                onClick={() => setSelected(selected === f.id ? null : f.id)}
                className="w-full text-left p-4 flex justify-between items-center"
              >
                <span className="font-mono text-sm">{f.source_file}</span>
                <span className="text-sm text-gray-500">
                  {f.tests_passed} passed / {f.tests_failed} failed — {f.coverage_pct}%
                </span>
              </button>
              {selected === f.id && (
                <pre className="p-4 bg-gray-50 text-sm overflow-x-auto border-t">
                  {f.test_content}
                </pre>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

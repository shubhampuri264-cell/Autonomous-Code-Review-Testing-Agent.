export interface Repository {
  id: string;
  user_id: string;
  github_url: string;
  default_branch: string;
  coverage_threshold: number;
  languages: string[];
  created_at: string;
  last_run_at: string | null;
}

export interface Run {
  id: string;
  repository_id: string;
  status: "pending" | "running" | "success" | "failed" | "timeout";
  trigger: "manual" | "webhook" | "scheduled";
  coverage_before: number | null;
  coverage_after: number | null;
  iterations: number;
  pr_url: string | null;
  error_message: string | null;
  started_at: string;
  completed_at: string | null;
}

export interface TestFile {
  id: string;
  run_id: string;
  source_file: string;
  test_file_path: string;
  test_content: string;
  tests_passed: number;
  tests_failed: number;
  coverage_pct: number;
}

export interface Correction {
  id: string;
  test_file_id: string;
  iteration: number;
  failure_summary: string;
  patch_applied: string;
  result: "resolved" | "unresolved" | "partial";
}

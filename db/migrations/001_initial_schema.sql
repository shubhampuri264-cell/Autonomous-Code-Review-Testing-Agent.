-- Initial schema for Autonomous Code Review & Testing Agent
-- Run against Supabase PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Table: repositories
-- ============================================
CREATE TABLE repositories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users NOT NULL,
    github_url TEXT NOT NULL,
    default_branch TEXT DEFAULT 'main',
    coverage_threshold INTEGER DEFAULT 80,
    languages TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_run_at TIMESTAMPTZ
);

-- RLS: users can only see their own repositories
ALTER TABLE repositories ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own repositories"
    ON repositories FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own repositories"
    ON repositories FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own repositories"
    ON repositories FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================
-- Table: runs
-- ============================================
CREATE TABLE runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id UUID REFERENCES repositories ON DELETE CASCADE NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'success', 'failed', 'timeout')),
    trigger TEXT DEFAULT 'manual' CHECK (trigger IN ('manual', 'webhook', 'scheduled')),
    coverage_before FLOAT,
    coverage_after FLOAT,
    iterations INTEGER DEFAULT 0,
    pr_url TEXT,
    error_message TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

ALTER TABLE runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view runs for own repos"
    ON runs FOR SELECT
    USING (
        repository_id IN (
            SELECT id FROM repositories WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert runs for own repos"
    ON runs FOR INSERT
    WITH CHECK (
        repository_id IN (
            SELECT id FROM repositories WHERE user_id = auth.uid()
        )
    );

-- ============================================
-- Table: test_files
-- ============================================
CREATE TABLE test_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES runs ON DELETE CASCADE NOT NULL,
    source_file TEXT NOT NULL,
    test_file_path TEXT NOT NULL,
    test_content TEXT NOT NULL,
    tests_passed INTEGER DEFAULT 0,
    tests_failed INTEGER DEFAULT 0,
    coverage_pct FLOAT DEFAULT 0.0
);

ALTER TABLE test_files ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view test files for own runs"
    ON test_files FOR SELECT
    USING (
        run_id IN (
            SELECT r.id FROM runs r
            JOIN repositories repo ON r.repository_id = repo.id
            WHERE repo.user_id = auth.uid()
        )
    );

-- ============================================
-- Table: corrections
-- ============================================
CREATE TABLE corrections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_file_id UUID REFERENCES test_files ON DELETE CASCADE NOT NULL,
    iteration INTEGER NOT NULL,
    failure_summary TEXT NOT NULL,
    patch_applied TEXT NOT NULL,
    result TEXT DEFAULT 'unresolved' CHECK (result IN ('resolved', 'unresolved', 'partial'))
);

ALTER TABLE corrections ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view corrections for own test files"
    ON corrections FOR SELECT
    USING (
        test_file_id IN (
            SELECT tf.id FROM test_files tf
            JOIN runs r ON tf.run_id = r.id
            JOIN repositories repo ON r.repository_id = repo.id
            WHERE repo.user_id = auth.uid()
        )
    );

-- ============================================
-- Indexes
-- ============================================
CREATE INDEX idx_runs_repository_id ON runs(repository_id);
CREATE INDEX idx_runs_status ON runs(status);
CREATE INDEX idx_test_files_run_id ON test_files(run_id);
CREATE INDEX idx_corrections_test_file_id ON corrections(test_file_id);

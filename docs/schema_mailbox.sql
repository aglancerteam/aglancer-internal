-- Mailbox table for Claude Code Teams–style inter-agent messaging.
-- Run in Supabase SQL editor if not using migrations.
CREATE TABLE IF NOT EXISTS mailbox (
  id BIGSERIAL PRIMARY KEY,
  from_agent_id TEXT NOT NULL,
  to_agent_id TEXT NOT NULL,
  task_id BIGINT REFERENCES tasks(id) ON DELETE SET NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  read_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_mailbox_to_agent ON mailbox(to_agent_id);
CREATE INDEX IF NOT EXISTS idx_mailbox_created_at ON mailbox(created_at DESC);

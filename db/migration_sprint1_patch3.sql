-- Sprint 1 Patch 3: add job_title to org_members
-- Run in Supabase Dashboard → SQL Editor

ALTER TABLE public.org_members ADD COLUMN IF NOT EXISTS job_title text;

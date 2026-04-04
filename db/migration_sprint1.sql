-- Sprint 1: Team/Org feature migration
-- Run this in Supabase Dashboard → SQL Editor

-- 1. Organizations
CREATE TABLE IF NOT EXISTS public.organizations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  created_by uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at timestamptz DEFAULT now()
);

-- 2. Org members
CREATE TABLE IF NOT EXISTS public.org_members (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id uuid NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role text NOT NULL DEFAULT 'member' CHECK (role IN ('admin', 'member')),
  visibility_consent boolean NOT NULL DEFAULT false,
  invited_at timestamptz DEFAULT now(),
  joined_at timestamptz,
  UNIQUE(org_id, user_id)
);

-- 3. Add org_id to invites
ALTER TABLE public.invites ADD COLUMN IF NOT EXISTS org_id uuid REFERENCES public.organizations(id) ON DELETE SET NULL;

-- 4. RLS for organizations
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "org members can read own org" ON public.organizations
  FOR SELECT USING (
    auth.uid() IN (
      SELECT user_id FROM public.org_members WHERE org_id = id
    )
  );

CREATE POLICY "org admin can update org" ON public.organizations
  FOR UPDATE USING (
    auth.uid() IN (
      SELECT user_id FROM public.org_members WHERE org_id = id AND role = 'admin'
    )
  );

CREATE POLICY "authenticated can create org" ON public.organizations
  FOR INSERT WITH CHECK (auth.uid() = created_by);

-- 5. RLS for org_members
ALTER TABLE public.org_members ENABLE ROW LEVEL SECURITY;

CREATE POLICY "org admin sees all members" ON public.org_members
  FOR SELECT USING (
    auth.uid() IN (
      SELECT user_id FROM public.org_members om2 WHERE om2.org_id = org_id AND om2.role = 'admin'
    )
  );

CREATE POLICY "member sees own record" ON public.org_members
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "member can update own consent" ON public.org_members
  FOR UPDATE USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Admins can insert members (via invite flow)
CREATE POLICY "service role can insert members" ON public.org_members
  FOR INSERT WITH CHECK (true);

-- 6. Helper function: get members with profiles (for HR dashboard)
-- Returns members who gave visibility_consent = true
CREATE OR REPLACE FUNCTION public.get_org_members_with_profiles(p_org_id uuid)
RETURNS TABLE (
  user_id uuid,
  role text,
  visibility_consent boolean,
  joined_at timestamptz,
  themes jsonb
) SECURITY DEFINER
SET search_path = public
LANGUAGE sql AS $$
  SELECT
    om.user_id,
    om.role,
    om.visibility_consent,
    om.joined_at,
    p.themes
  FROM org_members om
  LEFT JOIN profiles p ON p.user_id = om.user_id
  WHERE om.org_id = p_org_id
    AND (
      -- Admin calling: see all members
      EXISTS (
        SELECT 1 FROM org_members adm
        WHERE adm.org_id = p_org_id
          AND adm.user_id = auth.uid()
          AND adm.role = 'admin'
      )
      -- Member: only own record
      OR om.user_id = auth.uid()
    );
$$;

-- 7. Service role policy override for invites org_id update
-- (invites table should already have RLS disabled or admin policy)

-- Sprint 1 Patch 4: add job_title to RPC function
-- Run in Supabase Dashboard → SQL Editor

CREATE OR REPLACE FUNCTION public.get_org_members_with_profiles(p_org_id uuid)
RETURNS TABLE (
  user_id uuid,
  role text,
  job_title text,
  visibility_consent boolean,
  joined_at timestamptz,
  themes jsonb
) SECURITY DEFINER
SET search_path = public
LANGUAGE sql AS $$
  SELECT
    om.user_id,
    om.role,
    om.job_title,
    om.visibility_consent,
    om.joined_at,
    CASE WHEN om.visibility_consent THEN p.themes ELSE NULL END AS themes
  FROM org_members om
  LEFT JOIN profiles p ON p.user_id = om.user_id
  WHERE om.org_id = p_org_id
    AND (
      EXISTS (
        SELECT 1 FROM org_members adm
        WHERE adm.org_id = p_org_id
          AND adm.user_id = auth.uid()
          AND adm.role = 'admin'
      )
      OR om.user_id = auth.uid()
    );
$$;

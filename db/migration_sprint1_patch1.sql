-- Sprint 1 Patch 1: server-side consent enforcement in RPC
-- Run in Supabase Dashboard → SQL Editor

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
    -- Only expose themes if user gave consent; otherwise null
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

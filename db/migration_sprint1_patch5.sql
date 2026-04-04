-- Sprint 1 Patch 5: add display_name to org_members + populate real names
-- Run in Supabase Dashboard → SQL Editor

-- 1. Add display_name column
ALTER TABLE public.org_members
  ADD COLUMN IF NOT EXISTS display_name text;

-- 2. Populate real names by email (test org users)
UPDATE public.org_members om
SET display_name = u.display_name
FROM (
  SELECT au.id, n.display_name
  FROM auth.users au
  JOIN (VALUES
    ('irina@test-talents.dev',     'Ирина'),
    ('roman@test-talents.dev',     'Роман'),
    ('aleksandra@test-talents.dev','Александра'),
    ('sergey@test-talents.dev',    'Сергей'),
    ('ivan@test-talents.dev',      'Иван'),
    ('oksana@test-talents.dev',    'Оксана'),
    ('artem@test-talents.dev',     'Артём'),
    ('askar@test-talents.dev',     'Аскар')
  ) AS n(email, display_name) ON au.email = n.email
) u
WHERE om.user_id = u.id;

-- 3. Update RPC to return display_name
CREATE OR REPLACE FUNCTION public.get_org_members_with_profiles(p_org_id uuid)
RETURNS TABLE (
  user_id uuid,
  role text,
  job_title text,
  display_name text,
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
    om.display_name,
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

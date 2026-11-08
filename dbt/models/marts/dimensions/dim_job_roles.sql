with roles as (
    select role_family from {{ ref('role_rules') }}
    union select 'Other' as role_family
)
select {{ stable_key(['role_family']) }} as role_sk, role_family from roles

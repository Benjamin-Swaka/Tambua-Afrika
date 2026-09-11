"""
Department-scoped admin permissions.

This module is the single source of truth for how "custom admin dashboard"
access is decided once a staff account can be limited to one or more
departments, instead of the whole site.

Nothing here changes how the built-in Django /admin/ works -- that's still
gated by Django's own is_staff / is_superuser / permission system. This is
only about the *custom* dashboard under /dashboard/admin-panel/.

--------------------------------------------------------------------------
How "admin" now works, in three tiers:

1. Superuser
   Always has full, unrestricted access to every custom admin page,
   regardless of department memberships. This is the "main admin".

2. Full (site-wide) staff admin  -- THE EXISTING/LEGACY BEHAVIOUR
   A user with is_staff=True and NO DepartmentMembership rows where
   role='admin'. This is exactly what "Make Admin" has always done, so
   every staff account that existed before this feature keeps working
   exactly as it did -- nothing is taken away from them.

3. Department admin  -- THE NEW BEHAVIOUR
   A user with is_staff=True and one or more DepartmentMembership rows
   where role='admin'. As soon as a staff account is assigned to at
   least one department this way, their custom dashboard narrows to
   only the section(s) that belong to their assigned department(s).
   They can no longer see or modify sections for departments they are
   not assigned to.

This means simply granting "is_staff" (the old "Make Admin" button)
continues to behave exactly as before. Department-scoping only kicks in
once a department admin assignment is made, which is the new,
additive part of this feature.
"""

from functools import lru_cache

from core.models import Department, DepartmentMembership


# --------------------------------------------------------------------
# Which custom-admin "section" belongs to which department(s).
#
# Sections map 1:1 to the `segment` values already used across
# users/views.py + templates/users/*.html, so wiring this in doesn't
# require renaming anything that already exists.
#
# A section not listed here (e.g. admin_homepage, admin_users,
# admin_faqs, admin_chatbot, admin_messages) is treated as a
# site-wide / full-admin-only section -- it isn't tied to a single
# department's day-to-day content, so department admins don't get it.
# --------------------------------------------------------------------
SECTION_DEPARTMENTS = {
    'admin_submissions': ['ink', 'stage', 'comics'],
    'admin_tickets': ['stage'],
    'admin_manual_payments': ['stage'],
    'admin_shows': ['stage'],
    'admin_products': ['shop'],
}

# Submission.category -> department slug it belongs to. Used to filter
# the submissions queue for a department admin down to just the
# categories their department(s) own.
SUBMISSION_CATEGORY_DEPARTMENTS = {
    'manuscript': 'ink',
    'script': 'stage',
    'audition': 'stage',
    'comic': 'comics',
}

# Sections that are always site-wide, never department-scoped, even for
# a department admin. Kept explicit (rather than "everything not in
# SECTION_DEPARTMENTS") purely for readability/documentation.
FULL_ADMIN_ONLY_SECTIONS = {
    'admin_overview',
    'admin_homepage',
    'admin_users',
    'admin_faqs',
    'admin_chatbot',
    'admin_messages',
}


def get_admin_department_slugs(user):
    """
    Slugs of every department this user is an *admin* of (role='admin'
    in DepartmentMembership). Empty for anonymous users, superusers
    (who don't need it -- they already have full access) and regular
    staff who haven't been assigned to a department.
    """
    if not getattr(user, 'is_authenticated', False):
        return set()
    return set(
        DepartmentMembership.objects.filter(
            user=user, role='admin'
        ).values_list('department__slug', flat=True)
    )


def is_full_admin(user):
    """
    True for the "main admin" (superuser) and for any legacy/unscoped
    staff account -- i.e. is_staff=True with no department-admin
    assignments. This is what preserves existing behaviour: an account
    that only ever had "Make Admin" clicked on it keeps full access.
    """
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_superuser:
        return True
    if not user.is_staff:
        return False
    return len(get_admin_department_slugs(user)) == 0


def is_department_admin(user):
    """True for a staff account that is scoped to specific department(s)."""
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_superuser or not user.is_staff:
        return False
    return len(get_admin_department_slugs(user)) > 0


def can_access_section(user, section):
    """
    Can this user open the given custom-admin `segment`/section at all?
    Superusers and full admins: always yes. Department admins: only if
    the section belongs to one of their assigned departments.
    """
    if is_full_admin(user):
        return True
    if section in FULL_ADMIN_ONLY_SECTIONS:
        return False
    allowed_depts = SECTION_DEPARTMENTS.get(section)
    if not allowed_depts:
        # Unknown section with no explicit mapping -- fail closed.
        return False
    return bool(get_admin_department_slugs(user) & set(allowed_depts))


def allowed_submission_categories(user):
    """
    Which Submission.category values this user is allowed to see/manage.
    Returns None to mean "no restriction" (full admin).
    """
    if is_full_admin(user):
        return None
    dept_slugs = get_admin_department_slugs(user)
    return [
        category for category, dept in SUBMISSION_CATEGORY_DEPARTMENTS.items()
        if dept in dept_slugs
    ]


def admin_department_queryset():
    """All departments, for populating assignment checkboxes/selects."""
    return Department.objects.all().order_by('name')

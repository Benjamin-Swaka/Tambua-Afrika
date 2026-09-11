from .permissions import (
    get_admin_department_slugs,
    is_full_admin,
    is_department_admin,
)


def admin_scope(request):
    """
    Exposes department-admin scoping to every template, most importantly
    dashboard_base.html's sidebar, so the menu only shows links a
    department-scoped admin is actually allowed to open.

    Adds nothing for anonymous users / ordinary members -- this is only
    ever non-trivial for staff accounts.
    """
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated or not user.is_staff:
        return {
            'is_full_admin': False,
            'is_department_admin': False,
            'admin_department_slugs': set(),
        }

    return {
        'is_full_admin': is_full_admin(user),
        'is_department_admin': is_department_admin(user),
        'admin_department_slugs': get_admin_department_slugs(user),
    }

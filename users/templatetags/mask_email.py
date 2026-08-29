from django import template

register = template.Library()

@register.filter
def mask_email(email):
    if '@' not in email:
        return email
    local, domain = email.split('@', 1)
    masked_local = local[0] + '***' if len(local) > 1 else '***'
    return f"{masked_local}@{domain}"
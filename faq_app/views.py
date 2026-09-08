from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import FAQ, FAQCategory
from .forms import FAQForm


def faq_list(request):
    """Public premium FAQ page. Shows only active FAQs, grouped by category."""
    categories = FAQCategory.objects.prefetch_related("faqs").all()
    uncategorized = FAQ.objects.filter(category__isnull=True, is_active=True)

    visible_categories = []
    for cat in categories:
        active_faqs = cat.faqs.filter(is_active=True)
        if active_faqs.exists():
            visible_categories.append((cat, active_faqs))

    context = {
        "visible_categories": visible_categories,
        "uncategorized_faqs": uncategorized,
        # Staff get a single "Manage FAQs" link into the dashboard instead of
        # inline edit/delete controls scattered across the public page.
        "can_manage_faqs": request.user.is_authenticated and request.user.is_staff,
    }
    return render(request, "faq/faq_page.html", context)


# ── Dashboard-integrated management (no /admin/ login required) ──────────

@staff_member_required
def admin_faq_list(request):
    """Staff dashboard view: every FAQ (active and inactive), manageable inline."""
    faqs = FAQ.objects.select_related("category").all()
    context = {
        "faqs": faqs,
        "segment": "admin_faqs",
    }
    return render(request, "faq/admin_faq_list.html", context)


@staff_member_required
def faq_add(request):
    """Add a new FAQ from inside the dashboard."""
    if request.method == "POST":
        form = FAQForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "FAQ added successfully.")
            return redirect("admin_list")
    else:
        form = FAQForm()

    context = {"form": form, "mode": "add", "segment": "admin_faqs"}
    return render(request, "faq/admin_faq_form.html", context)


@staff_member_required
def faq_edit(request, pk):
    """Edit an existing FAQ from inside the dashboard."""
    faq = get_object_or_404(FAQ, pk=pk)
    if request.method == "POST":
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            messages.success(request, "FAQ updated successfully.")
            return redirect("admin_list")
    else:
        form = FAQForm(instance=faq)

    context = {"form": form, "mode": "edit", "faq": faq, "segment": "admin_faqs"}
    return render(request, "faq/admin_faq_form.html", context)


@staff_member_required
def faq_delete(request, pk):
    """Remove a FAQ, with a confirm step, from inside the dashboard."""
    faq = get_object_or_404(FAQ, pk=pk)
    if request.method == "POST":
        faq.delete()
        messages.success(request, "FAQ removed.")
        return redirect("admin_list")

    context = {"faq": faq, "segment": "admin_faqs"}
    return render(request, "faq/admin_faq_confirm_delete.html", context)

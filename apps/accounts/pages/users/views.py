from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from accounts.models import User
from accounts.models.agency import Agency
from .forms import CustomSetPasswordForm, UserForm, UserUpdateForm

from django.utils.safestring import mark_safe
from django.db.models import Q
import json
import re
from django.http import HttpResponse, QueryDict
from decorators import has_roles
from django.contrib.auth.decorators import login_required


@login_required
@has_roles(['admin', 'agencyuser'])
def user_list(request):
    """List all Users."""
    user_role = request.user.role
    if user_role == 'agencyuser' and not request.user.is_default_user:
        messages.error(request, "You don't have permission to view this page.")
        return redirect(request.META.get('HTTP_REFERER'))
    requested_html = re.search(r'^text/html', request.META.get('HTTP_ACCEPT'))
    if not requested_html:
        post_dict = QueryDict(request.POST.urlencode(), mutable=True)
        params_search = post_dict.get('columns')
        params_search_value = post_dict.get('search')
        param_start = max(int(request.POST.get('start', 0)), 0)
        param_limit = max(int(request.POST.get('length', 10)), 1)

        object_list = User.objects.all().order_by('-id')
        column_map = {
            1: 'email',
            2: 'full_name',
            3: 'role',
            4: 'agency__company_name',
            5: 'contact_no'
        }
        if user_role == 'agencyuser':
            object_list = object_list.filter(agency=request.user.agency)

        count = object_list.count()

        search_value = request.POST.get('search[value]', '')
        if search_value:
            object_list = object_list.filter(
                Q(email__icontains=search_value) |
                Q(full_name__icontains=search_value) |
                Q(role__icontains=search_value) |
                Q(agency__company_name__icontains=search_value) |
                Q(contact_no__icontains=search_value)
            )

        order_column_index = int(request.POST.get('order[0][column]', 0))
        order_dir = request.POST.get('order[0][dir]', 'desc')
        order_field = column_map.get(order_column_index, 'id')
        if order_dir == "asc":
            order_field = '-' + order_field

        filtered_total = object_list.count()
        object_list = object_list.order_by(
            order_field, '-id')[param_start:param_start + param_limit]
        object_list = object_list[param_start:param_limit + param_start]

        row = []
        for user in object_list:
            row.append({
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "agency": user.agency.company_name if user.agency else "",
                "contact_no": user.contact_no,
                "role": user.role,
                "is_blocked": user.is_blocked
            })

        context = {
            'draw': post_dict.get('draw'),
            'recordsTotal': count,
            'recordsFiltered': filtered_total,
            'data': row,
            "current": "users"
        }

        data = mark_safe(json.dumps(context, indent=4,
                         sort_keys=True, default=str))
        return HttpResponse(data, content_type='application/json')

    return render(request, "accounts/user/list.html", {"title": "User"})


@login_required
@has_roles(['admin'])
def user_create(request):
    """Create a new User."""
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                password = form.cleaned_data.get('password')
                user = form.save(commit=False)
                user.set_password(password)
                user.role = 'admin'
                user.save()
                messages.success(request, "Admin User created successfully!")
                return redirect("accounts:pages:user:list")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = UserForm()

    return render(request, "accounts/user/create.html", {"form": form, "title": "User"})


@login_required
@has_roles(['admin', 'agencyuser'])
def user_update(request, pk, agency_pk=None):
    """Update an existing User."""
    user = get_object_or_404(User, pk=pk)
    if request.user.role == 'agencyuser':
        if not request.user.is_default_user or user.agency != request.user.agency:
            messages.error(
                request, "You don't have permission to update this user.")
            return redirect(request.META.get('HTTP_REFERER'))
    agency = None
    if agency_pk:
        agency = get_object_or_404(Agency, pk=agency_pk)
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "User updated successfully!")
                if agency:
                    return redirect("accounts:pages:agency:detail", pk=agency.pk)
                return redirect("accounts:pages:user:list")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = UserUpdateForm(instance=user)

    return render(request, "accounts/user/update.html", {"form": form, "title": "User"})


@login_required
@has_roles(['admin', 'agencyuser'])
def user_block(request, pk):
    """Block a User."""
    user = get_object_or_404(User, pk=pk)
    if request.user.role == 'agencyuser':
        if not request.user.is_default_user or user.agency != request.user.agency:
            messages.error(
                request, "You don't have permission to block this user.")
            return redirect(request.META.get('HTTP_REFERER'))
    user.is_blocked = True
    user.save()
    messages.success(request, f"User {user.username} blocked successfully!")
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
@has_roles(['admin', "agencyuser"])
def change_password(request, pk, agency_pk=None):
    """ Change the password of user by admin"""
    user = get_object_or_404(User, pk=pk)
    agency = None
    if request.user.role == 'agencyuser':
        if not request.user.is_default_user:
            messages.error(
                request, "You don't have permission to change password of this user.")
            return redirect(request.META.get('HTTP_REFERER'))

        if user.agency != request.user.agency:
            messages.error(
                request, "You don't have permission to change password of this user.")
            return redirect(request.META.get('HTTP_REFERER'))

    if agency_pk:
        agency = get_object_or_404(Agency, pk=agency_pk)

    if request.method == "POST":
        form = CustomSetPasswordForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Password changed successfully!")
            if agency:
                return redirect("accounts:pages:agency:detail", pk=agency_pk)
            return redirect("accounts:pages:user:list")

    form = CustomSetPasswordForm(user=user)
    context = {
        "form": form,
        "user": user, "title": "User"
    }
    return render(request, "accounts/user/change_password.html", context)


@login_required
@has_roles(['admin', 'agencyuser'])
def user_unblock(request, pk):
    """Unblock a User."""
    user = get_object_or_404(User, pk=pk)
    if request.user.role == 'agencyuser':
        if not request.user.is_default_user and user.agency != request.user.agency:
            messages.error(
                request, "You don't have permission to unblock this user.")
            return redirect(request.META.get('HTTP_REFERER'))
    user.is_blocked = False
    user.save()
    messages.success(
        request, f"User {user.full_name or user.username} unblocked successfully!")
    return redirect(request.META.get('HTTP_REFERER', 'accounts:pages:user:list'))

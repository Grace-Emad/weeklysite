from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Activity, Enrollment, Profile
from .forms import ActivityForm, AccountCreateForm, AccountEditForm


def staff_required(view_func):
    """Only lets staff/admin accounts in - everyone else gets sent to login."""
    return user_passes_test(lambda u: u.is_authenticated and u.is_staff, login_url='login')(view_func)


# ---------- User-facing views ----------

def activity_list(request):
    """
    Shows every activity, how many spots are taken/left. Anyone can view
    this page - only enrolling/leaving/viewing score requires login.
    """
    activities = Activity.objects.all()
    my_enrolled_ids = set()
    if request.user.is_authenticated:
        my_enrolled_ids = set(
            Enrollment.objects.filter(user=request.user).values_list('activity_id', flat=True)
        )

    return render(request, 'activities/activity_list.html', {
        'activities': activities,
        'my_enrolled_ids': my_enrolled_ids,
    })


@login_required
def enroll(request, activity_id):
    """Enroll the logged-in user into an activity, if there's room."""
    activity = get_object_or_404(Activity, id=activity_id)

    if request.method == 'POST':
        if Enrollment.objects.filter(user=request.user, activity=activity).exists():
            messages.info(request, "You're already enrolled in this activity.")
        elif activity.is_full:
            messages.error(request, "Sorry, that activity is already full.")
        else:
            Enrollment.objects.create(user=request.user, activity=activity)
            profile = request.user.profile
            profile.score += activity.points
            profile.save()
            messages.success(request, f"You're enrolled in {activity.name}! +{activity.points} points")

    return redirect('activity_list')


@login_required
def unenroll(request, activity_id):
    """Let a user remove themselves from an activity they joined."""
    activity = get_object_or_404(Activity, id=activity_id)

    if request.method == 'POST':
        deleted, _ = Enrollment.objects.filter(user=request.user, activity=activity).delete()
        if deleted:
            profile = request.user.profile
            profile.score = max(profile.score - activity.points, 0)
            profile.save()
        messages.info(request, f"You've left {activity.name}.")

    return redirect('activity_list')


@login_required
def my_score(request):
    """Shows the user's current score and everything they're enrolled in."""
    profile = request.user.profile
    my_enrollments = Enrollment.objects.filter(user=request.user).select_related('activity')

    return render(request, 'activities/my_score.html', {
        'profile': profile,
        'my_enrollments': my_enrollments,
    })


# ---------- Admin views (staff only) ----------

@staff_required
def admin_dashboard(request):
    """Landing page for admins: quick links + a list of all activities."""
    activities = Activity.objects.all()
    return render(request, 'activities/admin_dashboard.html', {'activities': activities})


@staff_required
def admin_activity_create(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Activity created.")
            return redirect('admin_dashboard')
    else:
        form = ActivityForm()

    return render(request, 'activities/admin_activity_form.html', {
        'form': form, 'title': 'New activity',
    })


@staff_required
def admin_activity_edit(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)

    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, "Activity updated.")
            return redirect('admin_dashboard')
    else:
        form = ActivityForm(instance=activity)

    return render(request, 'activities/admin_activity_form.html', {
        'form': form, 'title': f'Edit {activity.name}',
    })


@staff_required
def admin_activity_delete(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)

    if request.method == 'POST':
        activity.delete()
        messages.info(request, "Activity deleted.")
        return redirect('admin_dashboard')

    return render(request, 'activities/admin_confirm_delete.html', {
        'object_label': activity.name,
        'cancel_url': 'admin_dashboard',
    })


@staff_required
def admin_account_list(request):
    accounts = User.objects.select_related('profile').all()
    return render(request, 'activities/admin_account_list.html', {'accounts': accounts})


@staff_required
def admin_account_create(request):
    if request.method == 'POST':
        form = AccountCreateForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            user.is_staff = form.cleaned_data['is_staff']
            user.save()
            messages.success(request, f"Account '{user.username}' created.")
            return redirect('admin_account_list')
    else:
        form = AccountCreateForm()

    return render(request, 'activities/admin_account_form.html', {'form': form})


@staff_required
def admin_account_detail(request, user_id):
    """
    Edit an account's score/admin access, and manage which activities
    they're enrolled in - all from one page.
    """
    account = get_object_or_404(User, id=user_id)
    profile, _ = Profile.objects.get_or_create(user=account)
    all_activities = Activity.objects.all()
    enrolled_ids = set(
        Enrollment.objects.filter(user=account).values_list('activity_id', flat=True)
    )

    if request.method == 'POST':
        form = AccountEditForm(request.POST)
        if form.is_valid():
            profile.score = form.cleaned_data['score']
            profile.save()
            account.is_staff = form.cleaned_data['is_staff']
            account.save()

            submitted_ids = set(int(i) for i in request.POST.getlist('activities'))
            for activity in all_activities:
                currently_enrolled = activity.id in enrolled_ids
                should_be_enrolled = activity.id in submitted_ids
                if should_be_enrolled and not currently_enrolled:
                    Enrollment.objects.create(user=account, activity=activity)
                elif currently_enrolled and not should_be_enrolled:
                    Enrollment.objects.filter(user=account, activity=activity).delete()

            messages.success(request, f"Updated {account.username}.")
            return redirect('admin_account_list')
    else:
        form = AccountEditForm(initial={'score': profile.score, 'is_staff': account.is_staff})

    return render(request, 'activities/admin_account_detail.html', {
        'account': account,
        'form': form,
        'all_activities': all_activities,
        'enrolled_ids': enrolled_ids,
    })


@staff_required
def admin_account_delete(request, user_id):
    account = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        account.delete()
        messages.info(request, "Account deleted.")
        return redirect('admin_account_list')

    return render(request, 'activities/admin_confirm_delete.html', {
        'object_label': account.username,
        'cancel_url': 'admin_account_list',
    })
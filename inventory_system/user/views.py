from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from .models import Profile
from user.forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_protect
from orders.models import Invoice, cart, cart_records, customerOrderHistory, OrderAmount


def logout(request):
    return render(request, 'users/login.html')

# custom 404 view
def custom_404(request, exception):
    return render(request, 'users/404.html', status=404)


class RegisterView(View):
    group_name = ''  # Provide a default value
    
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)  # Save the form data but don't commit to the database yet
            
            role = form.cleaned_data['role']

            group_name = ''

            if role == 'customer':
                group_name = 'customer'
            elif role == 'admin':
                group_name = 'admin'
            elif role == 'farmer':
                group_name = 'farmer'

            try:
                group = Group.objects.get(name=group_name)
            except ObjectDoesNotExist:
                # Create the group if it doesn't exist
                group = Group.objects.create(name=group_name)

            if role == 'admin':
                user.is_superuser = True
                user.is_staff = True

            user.save()  # Now commit the changes to the database

            user.groups.add(group)  # Add the user to the group after saving

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})

# Class based view that extends from the built in login view to add a remember me functionality
class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('home')


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('home')


@login_required
def profile(request):
    # view profile details
    logged_user = request.user
    profile_info = Profile.objects.get(user_id=logged_user.id)
    
    # edit profile details
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():

            user_form.save()
            profile_form.save()
            

        messages.success(request, 'Your profile is updated successfully')
        return redirect(to='users-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)
    
    # update order management
    customer_name = request.session['old_username']
    Invoice.objects.filter(billing_name=customer_name).update(billing_email=logged_user.email)
    cart.objects.filter(customer=customer_name).update(customer=request.user.username)
    customerOrderHistory.objects.filter(customer=customer_name).update(customer=request.user.username)
    cart_records.objects.filter(customer=customer_name).update(customer=request.user.username)
    OrderAmount.objects.filter(customer=customer_name).update(customer=request.user.username)
    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form, 'profile': profile_info, 'user': logged_user})

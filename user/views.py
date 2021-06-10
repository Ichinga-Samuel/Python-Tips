from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils import safestring
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth import login, get_user_model
from django.http import HttpResponse
from django.conf import settings
from django.views.generic import DetailView

from tips.models import Tips
from .forms import UserRegistrationForm
from .forms import ProfileForm
User = get_user_model()


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (

            safestring.SafeText(user.pk) + safestring.SafeText(timestamp) +
            safestring.SafeText(user.profile.verified)
        )


account_activation_token = AccountActivationTokenGenerator()


class UserDetail(DetailView):
    model = User
    template_name = 'user/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['tips'] = Tips.objects.all()[:10]
        if hasattr(self.object, 'profile'):
            context['profile'] = self.object.profile
        return context


def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            current_site = get_current_site(request)
            context1 = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            }
            subject = 'Activate Your Daily Python Tips Account'
            html_msg = render_to_string('user/activation/account_activation_email.html', context1)
            message = render_to_string('user/activation/account_activation_text.html', context1)
            try:
                user.email_user(subject, message, html_message=html_msg)
                return redirect('user:activation_sent')
            except Exception as e:
                print(e)
                return redirect('user:activation_unsuccessful')
    else:
        form = UserRegistrationForm()
    return render(request, 'user/signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.profile.verified = True
        user.save()
        login(request, user)
        return redirect('home:home_page')
    else:
        return render(request, 'user/activation/account_activation_invalid.html')


def activation_sent(request):
    return render(request, "user/activation/activation_sent.html")


def activation_not_sent(request):
    return render(request, 'activation/activation_not_sent.html')
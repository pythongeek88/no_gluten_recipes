from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Tutorial, TutorialCategory, TutorialSeries
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from .forms import NewUserForm

# Create your views here.
def homepage(request):
    return render(request=request,
                  template_name='main/categories.html',
                  context={"categories": TutorialCategory.objects.all})


def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New account created: {username}")
            login(request, user)
            return redirect("main:homepage")

        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

            return render(request = request,
                          template_name = "main/register.html",
                          context={"form":form})

    form = NewUserForm
    return render(request = request,
                  template_name = "main/register.html",
                  context={"form":form})

def logout_request(request):
    logout(request)
    messages.info(request, "logged out successfully!")
    return redirect("main:homepage")    

def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect('/')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request = request,
                    template_name = "main/login.html",
                    context={"form":form})


def single_slug(request, single_slug):
    # first check to see if the url is in categories.

    categories = [c.category_slug for c in TutorialCategory.objects.all()]
    if single_slug in categories:
        matching_series = TutorialSeries.objects.filter(tutorial_category__category_slug=single_slug)
        series_urls = {}

        for m in matching_series.all():
            this_series_tutorials = Tutorial.objects.filter(tutorial_series__tutorial_series=m.tutorial_series)
            if this_series_tutorials:
                part_one = this_series_tutorials.earliest("tutorial_published")
                series_urls[m] = part_one.tutorial_slug

        return render(request=request,
                        template_name='main/category.html',
                        context={"tutorial_series": matching_series, "part_ones": series_urls})
    else:
        return render(request=request, template_name='main/category.html')

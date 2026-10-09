from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import CarOwnerForm, CarOwnerUserCreationForm, LoginForm
from .models import Car, CarOwner


def staff_required(view):
    return user_passes_test(
        lambda user: user.is_authenticated and user.is_staff,
        login_url="auth",
    )(view)


class StaffRequiredMixin(UserPassesTestMixin):
    login_url = "auth"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff


def auth_page(request):
    if request.user.is_authenticated:
        return redirect("owner_list")

    login_form = LoginForm()
    register_form = CarOwnerUserCreationForm()
    active_tab = request.GET.get("tab", "login")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "login":
            login_form = LoginForm(request, data=request.POST)
            active_tab = "login"
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect("owner_list")

        elif action == "register":
            register_form = CarOwnerUserCreationForm(request.POST)
            active_tab = "register"
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                return redirect("owner_list")

    return render(
        request,
        "auth.html",
        {
            "login_form": login_form,
            "register_form": register_form,
            "active_tab": active_tab,
        },
    )


def logout_view(request):
    logout(request)
    return redirect("auth")


def owner_detail(request, owner_id):
    owner = get_object_or_404(CarOwner, pk=owner_id)
    return render(request, "owner.html", {"owner": owner})


def owner_list(request):
    owners = CarOwner.objects.all().order_by("id")
    return render(request, "owner_list.html", {"owners": owners})


@staff_required
def owner_create(request):
    if request.method == "POST":
        form = CarOwnerForm(request.POST)
        if form.is_valid():
            owner = form.save(commit=False)
            owner.set_unusable_password()
            owner.save()
            return redirect("owner_list")
    else:
        form = CarOwnerForm()

    return render(request, "owner_form.html", {"form": form})


class CarListView(ListView):
    model = Car
    template_name = "project_first_app/car_list.html"
    context_object_name = "cars"


class CarDetailView(DetailView):
    model = Car
    template_name = "project_first_app/car_detail.html"
    context_object_name = "car"


class CarCreateView(StaffRequiredMixin, CreateView):
    model = Car
    fields = ["state_number", "brand", "model", "color"]
    template_name = "project_first_app/car_form.html"
    success_url = reverse_lazy("car_list")


class CarUpdateView(StaffRequiredMixin, UpdateView):
    model = Car
    fields = ["state_number", "brand", "model", "color"]
    template_name = "project_first_app/car_form.html"
    success_url = reverse_lazy("car_list")


class CarDeleteView(StaffRequiredMixin, DeleteView):
    model = Car
    template_name = "project_first_app/car_confirm_delete.html"
    success_url = reverse_lazy("car_list")

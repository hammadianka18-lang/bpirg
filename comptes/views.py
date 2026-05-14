from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def login_view(request):
    """
    Vue de connexion utilisateur
    """

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            # Redirection vers le dashboard des ressources génétiques
            return redirect("ressources_genetiques:dashboard")

        else:
            messages.error(
                request,
                "❌ Nom d'utilisateur ou mot de passe incorrect."
            )

    return render(request, "comptes/login.html")


def logout_view(request):
    """
    Vue de déconnexion utilisateur
    """
    logout(request)
    messages.success(
        request,
        "✅ Vous avez été déconnecté avec succès."
    )

    return redirect("home")
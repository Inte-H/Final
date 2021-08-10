from django.shortcuts import render


def landing(request):
    return render(
        request,
        'page/landing.html',
    )


def about_me(request):
    return render(
        request,
        'page/about_me.html',
    )

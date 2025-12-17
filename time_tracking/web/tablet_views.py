from django.shortcuts import render



def tablet_home(request):
    return render(request, "tablet/index.html")


def tablet_scan(request):
    mode = request.GET.get("mode")  # register | status | action
    action = request.GET.get("action")  # CHECK_IN, BREAK_START itd.
    return render(request, "tablet/scan.html", {
        "mode": mode,
        "action": action,
    })


def tablet_message(request):
    message = request.GET.get("message", "")
    return render(request, "tablet/message.html", {
        "message": message
    })


def tablet_status(request):
    return render(request, "tablet/status.html")

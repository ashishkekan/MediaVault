# gallery/context_processors.py  ← new file banao


def theme(request):
    return {"is_light_mode": request.session.get("theme") == "light"}

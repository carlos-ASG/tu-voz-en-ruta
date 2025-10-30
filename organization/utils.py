def build_tenant_url(scheme, domain, port=None, path=None):
    """Construye la URL completa del tenant con el esquema y dominio proporcionados."""
    redirect_url = f"{scheme}://{domain}"
    if port and port == '8000': # se agrega el puerto solo si esta en modo desarrollo
        redirect_url += f":{port}"
    if path:
        redirect_url += path
    redirect_url += '/'
    return redirect_url

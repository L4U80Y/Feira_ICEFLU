# feira_app/middleware.py

class DebugCSRFMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Imprime os cabeçalhos relevantes antes de a verificação CSRF acontecer
        # Iremos procurar por estas linhas nos logs do Cloud Run
        print("--- [CSRF DEBUG] INICIANDO REQUISIÇÃO ---")
        print(f"[CSRF DEBUG] Método: {request.method}")
        print(f"[CSRF DEBUG] Caminho: {request.path}")
        print(f"[CSRF DEBUG] Host recebido: {request.META.get('HTTP_HOST')}")
        print(f"[CSRF DEBUG] Cabeçalho Referer: {request.META.get('HTTP_REFERER')}")
        print(f"[CSRF DEBUG] É seguro (is_secure()): {request.is_secure()}")
        print(f"[CSRF DEBUG] Cookie CSRF enviado pelo navegador: {request.COOKIES.get('csrftoken')}")
        print("--- [CSRF DEBUG] FIM DA REQUISIÇÃO ---")

        response = self.get_response(request)
        return response
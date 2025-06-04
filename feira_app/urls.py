# feira_app/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views # Django's built-in views
from . import views

app_name = 'feira_app'

urlpatterns = [
    # URLs de Autenticação (usando as views do Django)
    path('login/', auth_views.LoginView.as_view(template_name='feira_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='feira_app:login'), name='logout'), # Redireciona para login após sair

    # URLs da Área do Beneficiário
    path('produtos/', views.produto_list_view, name='produto_list'),
    path('minha-lista/', views.minha_lista_view, name='minha_lista'),
    path('lista/adicionar/<int:produto_id>/', views.add_to_list_view, name='add_to_list'),
    path('lista/item/atualizar/<int:item_id>/', views.update_list_item_view, name='update_list_item'),
    path('lista/item/remover/<int:item_id>/', views.remove_from_list_view, name='remove_from_list'),

    # Você pode adicionar uma view de entrada/home aqui se necessário
    path('', views.produto_list_view, name='home'), # Exemplo: home redireciona para lista de produtos
]
from django.db import models
from django.conf import settings # Para ForeignKey para o User do Django
from django.utils import timezone
from decimal import Decimal

# É altamente recomendável usar o sistema de autenticação do Django.
# Se os beneficiários também são usuários que fazem login no sistema,
# considere criar um Perfil que se relaciona OneToOne com o User do Django
# ou estender o AbstractUser.
# Exemplo de Perfil (se Beneficiario for um perfil do User):
# class Beneficiario(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     beneficio_mensal = models.DecimalField(max_digits=10, decimal_places=2)
#     # is_admin pode ser verificado com user.is_staff ou user.is_superuser
#
#     def __str__(self):
#         return self.user.username

# No entanto, seguindo a estrutura solicitada diretamente:
class Beneficiario(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    # Se for usar o sistema de login do Django, o campo 'email' e 'senha'
    # seriam gerenciados pelo modelo User do Django.
    # Se este modelo Beneficiario for representar um usuário que faz login,
    # o ideal é usar um OneToOneField para o User do Django ou estender AbstractUser.
    # Por ora, vou manter como solicitado, mas com ressalvas.
    email = models.EmailField(unique=True, verbose_name="E-mail")
    # NUNCA armazene senhas em texto plano. O Django User model cuida disso.
    # Se for um campo de senha customizado, a lógica de hashing deve ser implementada.
    # senha_hash = models.CharField(max_length=128, verbose_name="Senha HASH") # Exemplo, não recomendado fazer manualmente
    beneficio_mensal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Benefício Mensal (R$)"
    )
    is_admin = models.BooleanField(
        default=False,
        verbose_name="É Administrador?"
    )
    # Adicionando campos de data para rastreamento (boa prática)
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    class Meta:
        verbose_name = "Beneficiário"
        verbose_name_plural = "Beneficiários"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome do Produto")
    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço Unitário (R$)"
    )
    unidade_medida = models.CharField(
        max_length=50,
        blank=True, # Opcional
        null=True,  # Opcional
        verbose_name="Unidade de Medida",
        help_text="Ex: Kg, Unidade, Litro, Dúzia"
    )
    disponivel = models.BooleanField(
        default=True,
        verbose_name="Disponível?"
    )
    # Adicionando campos de data para rastreamento
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} (R$ {self.preco_unitario})"

class ListaDeCompra(models.Model):
    STATUS_CHOICES = [
        ('aberta', 'Em Aberto'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]

    # Se você estiver usando o modelo Beneficiario customizado acima:
    beneficiario = models.ForeignKey(
        Beneficiario,
        on_delete=models.PROTECT, # Evita excluir beneficiário se ele tiver listas
        related_name="listas_de_compra",
        verbose_name="Beneficiário"
    )
    # Se estivesse usando o User do Django via um perfil Beneficiario:
    # beneficiario = models.ForeignKey(
    #     settings.AUTH_USER_MODEL, # Ou o seu modelo de Perfil
    #     on_delete=models.PROTECT,
    #     related_name="listas_de_compra"
    # )
    data_criacao = models.DateTimeField(
        default=timezone.now, # Permite ser editado no admin se não for auto_now_add
        verbose_name="Data de Criação"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='aberta',
        verbose_name="Status da Lista"
    )
    limite_compra_calculado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Limite de Compra Calculado (R$)",
        help_text="Limite da compra no momento da criação da lista (3x benefício mensal)"
    )
    # Adicionando campo de data para rastreamento
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Lista de Compra"
        verbose_name_plural = "Listas de Compra"
        ordering = ['-data_criacao', 'beneficiario']

    def __str__(self):
        return f"Lista de {self.beneficiario.nome} - {self.data_criacao.strftime('%d/%m/%Y')}"

    @property
    def total_lista(self):
        """Calcula o total dos itens na lista."""
        total = self.itens_da_lista.aggregate(
            total_calculado=models.Sum(models.F('quantidade') * models.F('preco_unitario_no_momento'))
        )['total_calculado']
        return total or 0.00

class ItemDaLista(models.Model):
    lista = models.ForeignKey(
        ListaDeCompra,
        on_delete=models.CASCADE,
        related_name="itens_da_lista",
        verbose_name="Lista de Compra"
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        verbose_name="Produto"
    )
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade")
    preco_unitario_no_momento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço Unitário no Momento da Compra (R$)",
        help_text="Preço do produto no momento em que foi adicionado à lista"
    )

    class Meta:
        verbose_name = "Item da Lista"
        verbose_name_plural = "Itens da Lista"
        unique_together = ('lista', 'produto')
        ordering = ['produto__nome']

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} na lista de {self.lista.beneficiario.nome}"

    @property
    def subtotal(self): # Esta é a propriedade a ser modificada (provavelmente linha 169)
        if self.quantidade is not None and self.preco_unitario_no_momento is not None:
            return self.quantidade * self.preco_unitario_no_momento
        return Decimal('0.00') # Retorna 0.00 se algum dos valores for None
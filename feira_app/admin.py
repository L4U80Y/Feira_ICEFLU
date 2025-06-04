from django.contrib import admin
from .models import Beneficiario, Produto, ListaDeCompra, ItemDaLista
from decimal import Decimal

# Customização para o modelo Beneficiario
class BeneficiarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'beneficio_mensal', 'is_admin', 'data_criacao', 'data_atualizacao')
    search_fields = ('nome', 'email')
    list_filter = ('is_admin', 'data_criacao')
    readonly_fields = ('data_criacao', 'data_atualizacao') # Campos que não devem ser editados manualmente no admin
    fieldsets = (
        (None, {
            'fields': ('nome', 'email', 'beneficio_mensal', 'is_admin')
        }),
        ('Datas de Controle', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',) # Para agrupar e recolher esta seção
        }),
    )

# Customização para o modelo Produto
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco_unitario', 'unidade_medida', 'disponivel', 'data_atualizacao')
    search_fields = ('nome',)
    list_filter = ('disponivel', 'unidade_medida')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    fieldsets = (
        (None, {
            'fields': ('nome', 'preco_unitario', 'unidade_medida', 'disponivel')
        }),
        ('Datas de Controle', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

# Inline para ItemDaLista, para ser usado dentro de ListaDeCompraAdmin
class ItemDaListaInline(admin.TabularInline): # ou admin.StackedInline para um layout diferente
    model = ItemDaLista
    fields = ('produto', 'quantidade', 'preco_unitario_no_momento', 'subtotal_display')
    readonly_fields = ('subtotal_display',) # Para mostrar o subtotal calculado
    extra = 1 # Quantidade de formulários extras para adicionar itens

    def subtotal_display(self, obj):
        return obj.subtotal
    subtotal_display.short_description = "Subtotal (R$)"

# Customização para o modelo ListaDeCompra
class ListaDeCompraAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'beneficiario', 'status', 'limite_compra_calculado', 'total_da_lista_display', 'data_criacao', 'data_atualizacao')
    list_filter = ('status', 'data_criacao', 'beneficiario')
    search_fields = ('beneficiario__nome', 'beneficiario__email')
    readonly_fields = ('data_criacao', 'data_atualizacao', 'total_da_lista_display', 'limite_compra_calculado')
    inlines = [ItemDaListaInline]
    fieldsets = (
        (None, {
            'fields': ('beneficiario', 'status', 'limite_compra_calculado', 'total_da_lista_display')
        }),
        ('Datas de Controle', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

    def total_da_lista_display(self, obj):
        return obj.total_lista
    total_da_lista_display.short_description = "Total da Lista (R$)"

    # ---- ADICIONE ESTE MÉTODO ----
    def save_model(self, request, obj, form, change):
        # obj é a instância de ListaDeCompra
        # change é um booleano: True se for um modelo existente sendo alterado,
        # False se for um novo modelo sendo adicionado.

        if not change: # Se é um novo objeto sendo adicionado
            if obj.beneficiario: # Garante que um beneficiário foi selecionado
                try:
                    # Certifique-se de que obj.beneficiario.beneficio_mensal é um Decimal
                    beneficio = Decimal(obj.beneficiario.beneficio_mensal or 0)
                    obj.limite_compra_calculado = beneficio * Decimal('3.00')
                except TypeError:
                    # Caso beneficio_mensal seja None, defina um limite padrão ou levante um erro mais específico
                    # Para este exemplo, vamos definir como 0 se não puder calcular.
                    # O ideal é garantir que beneficio_mensal sempre tenha um valor.
                    obj.limite_compra_calculado = Decimal('0.00')
                    # Você pode querer adicionar uma mensagem de erro aqui, se aplicável
                    # from django.contrib import messages
                    # messages.warning(request, "Benefício mensal do beneficiário não definido. Limite calculado como 0.")

        super().save_model(request, obj, form, change) # Chama o método save_model da classe pai para salvar o objeto

# Customização para o modelo ItemDaLista (opcional, pois é gerenciado inline)
# Se você quiser também uma view separada para ItensDaLista:
class ItemDaListaAdmin(admin.ModelAdmin):
    list_display = ('lista', 'produto', 'quantidade', 'preco_unitario_no_momento', 'subtotal_display')
    search_fields = ('produto__nome', 'lista__beneficiario__nome')
    list_filter = ('produto',)
    readonly_fields = ('subtotal_display',)

    def subtotal_display(self, obj):
        return obj.subtotal
    subtotal_display.short_description = "Subtotal (R$)"


# Registrando os modelos com suas respectivas classes Admin (ou sem, para o padrão)
admin.site.register(Beneficiario, BeneficiarioAdmin)
admin.site.register(Produto, ProdutoAdmin)
admin.site.register(ListaDeCompra, ListaDeCompraAdmin)

# Opcional: registrar ItemDaLista separadamente se desejar uma interface de admin dedicada para ele,
# além da gestão inline. Geralmente, se é apenas um item de detalhe, o inline é suficiente.
# Se você não precisar de uma página de admin separada para ItensDaLista, pode comentar a linha abaixo.
admin.site.register(ItemDaLista, ItemDaListaAdmin)
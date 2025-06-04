# feira_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.urls import reverse # MANTENHA O REVERSE
from .models import Produto, Beneficiario, ListaDeCompra, ItemDaLista
from .forms import AddToListForm, UpdateListItemForm
from decimal import Decimal

# Helper para obter o Beneficiario
def get_beneficiario_atual(user):
    if not user.is_authenticated:
        return None
    try:
        # A forma ideal aqui seria ter um link OneToOneField do User para Beneficiario
        # ex: return user.perfil_beneficiario
        # Ou se Beneficiario fosse seu User model customizado: return user
        # A solução abaixo (baseada no email) é um fallback e depende da consistência dos dados.
        return Beneficiario.objects.get(email=user.email)
    except Beneficiario.DoesNotExist:
        messages.warning(user, "Perfil de beneficiário não encontrado para o email associado ao seu usuário.") # Adicionando user ao messages
        return None
    except AttributeError: # Caso user não tenha o atributo email (improvável para User padrão)
        messages.error(user, "Erro ao tentar obter informações do usuário para buscar o perfil de beneficiário.") # Adicionando user ao messages
        return None


@login_required
def get_or_create_active_lista(request): # request é passado aqui
    beneficiario = get_beneficiario_atual(request.user) # request.user já é o usuário
    if not beneficiario:
        # A mensagem de erro já foi (ou deveria ser) enviada por get_beneficiario_atual
        # Se quiser adicionar uma mensagem específica aqui:
        # messages.error(request, "Não foi possível obter ou criar a lista pois o perfil de beneficiário não foi encontrado.")
        return None

    # Garante que beneficio_mensal seja um Decimal para o cálculo, tratando None como 0
    beneficio_valor = beneficiario.beneficio_mensal if beneficiario.beneficio_mensal is not None else Decimal('0.00')

    lista, created = ListaDeCompra.objects.get_or_create(
        beneficiario=beneficiario,
        status='aberta',
        defaults={'limite_compra_calculado': beneficio_valor * Decimal('3.00')}
    )
    # A lógica para atualizar o limite se o benefício mudar foi comentada,
    # mantendo o limite fixo no momento da criação, como discutido.
    return lista

@login_required
def produto_list_view(request):
    produtos = Produto.objects.filter(disponivel=True)
    add_form = AddToListForm()
    lista_ativa = get_or_create_active_lista(request)
    beneficiario_atual = get_beneficiario_atual(request.user)

    context = {
        'produtos': produtos,
        'add_form': add_form,
        'lista_ativa': lista_ativa,
        'beneficiario': beneficiario_atual
    }
    return render(request, 'feira_app/produto_list.html', context)

@login_required
@transaction.atomic
def add_to_list_view(request, produto_id):
    if request.method == 'POST':
        produto = get_object_or_404(Produto, id=produto_id, disponivel=True)
        form = AddToListForm(request.POST)
        lista_compra = get_or_create_active_lista(request)

        if not lista_compra:
            return redirect('feira_app:produto_list') # ou uma página de erro

        if form.is_valid():
            quantidade = form.cleaned_data['quantidade'] # int

            # --- INÍCIO DAS CORREÇÕES PARA TypeError ---
            # Garante que preco_no_momento é Decimal
            preco_no_momento = Decimal(str(produto.preco_unitario))

            # Garanta que a multiplicação resulte em Decimal
            custo_novo_item = preco_no_momento * Decimal(quantidade)

            # Garanta que total_atual_lista é Decimal
            total_atual_lista = Decimal(str(lista_compra.total_lista))

            # Garanta que limite_compra_calculado é Decimal (já é um DecimalField, mas converter str para segurança)
            limite_calculado = Decimal(str(lista_compra.limite_compra_calculado))
            # --- FIM DAS CORREÇÕES PARA TypeError ---

            if (total_atual_lista + custo_novo_item) > limite_calculado:
                messages.error(request, f"Não foi possível adicionar {produto.nome}. Limite de R$ {limite_calculado:.2f} seria excedido.")
            else:
                item_existente, created = ItemDaLista.objects.get_or_create(
                    lista=lista_compra,
                    produto=produto,
                    defaults={'quantidade': quantidade, 'preco_unitario_no_momento': preco_no_momento}
                )
                if not created:
                    nova_quantidade = item_existente.quantidade + quantidade

                    # --- INÍCIO DAS CORREÇÕES PARA TypeError (bloco item existente) ---
                    preco_item_existente = Decimal(str(item_existente.preco_unitario_no_momento))

                    novo_subtotal_item_existente = Decimal(nova_quantidade) * preco_item_existente
                    subtotal_antigo_item_existente = Decimal(item_existente.quantidade) * preco_item_existente
                    
                    aumento_custo = novo_subtotal_item_existente - subtotal_antigo_item_existente
                    # --- FIM DAS CORREÇÕES PARA TypeError (bloco item existente) ---

                    if (total_atual_lista + aumento_custo) > limite_calculado:
                        messages.error(request, f"Não foi possível adicionar mais unidades de {produto.nome}. Limite de R$ {limite_calculado:.2f} seria excedido.")
                    else:
                        item_existente.quantidade = nova_quantidade
                        item_existente.save()
                        messages.success(request, f"{quantidade} unidade(s) de {produto.nome} adicionada(s) à lista.")
                else:
                    messages.success(request, f"{produto.nome} adicionado à lista.")
        else:
            messages.error(request, "Erro ao adicionar produto. Quantidade inválida ou dados incorretos.")
        
        # Redireciona para a página de onde o usuário veio (lista de produtos ou minha lista) ou fallback
        return redirect(request.META.get('HTTP_REFERER', reverse('feira_app:produto_list')))
    # Se não for POST, redireciona para a lista de produtos (ou outra página apropriada)
    return redirect('feira_app:produto_list')


@login_required
def minha_lista_view(request):
    lista_compra = get_or_create_active_lista(request)
    if not lista_compra:
        return redirect(reverse('feira_app:login')) 

    itens_lista = ItemDaLista.objects.filter(lista=lista_compra).select_related('produto')
    beneficiario = get_beneficiario_atual(request.user)

    itens_com_forms = []
    for item in itens_lista:
        form_para_item = UpdateListItemForm(initial={'quantidade': item.quantidade})
        itens_com_forms.append({
            'item_obj': item,
            'update_form': form_para_item
        })

    # --- ADICIONE O CÁLCULO DO LIMITE RESTANTE AQUI ---
    limite_restante = Decimal('0.00') # Valor padrão
    if lista_compra and lista_compra.limite_compra_calculado is not None:
        # Garante que ambos são Decimal antes de subtrair
        limite_calculado_decimal = Decimal(str(lista_compra.limite_compra_calculado))
        total_lista_decimal = Decimal(str(lista_compra.total_lista)) # total_lista já deve ser Decimal pela property
        limite_restante = limite_calculado_decimal - total_lista_decimal

    context = {
        'lista_compra': lista_compra,
        'itens_com_forms': itens_com_forms,
        'beneficiario': beneficiario,
        'limite_restante': limite_restante, # <--- PASSE PARA O CONTEXTO
    }
    return render(request, 'feira_app/minha_lista.html', context)


@login_required
@transaction.atomic
def update_list_item_view(request, item_id):
    item = get_object_or_404(ItemDaLista, id=item_id)
    lista_compra = item.lista
    beneficiario_atual = get_beneficiario_atual(request.user)

    if not beneficiario_atual or lista_compra.beneficiario != beneficiario_atual:
        messages.error(request, "Acesso não autorizado.")
        return redirect('feira_app:minha_lista')

    if request.method == 'POST':
        form = UpdateListItemForm(request.POST)
        if form.is_valid():
            nova_quantidade = form.cleaned_data['quantidade']
            
            # --- INÍCIO DAS CORREÇÕES PARA TypeError ---
            # Garanta que os valores sejam Decimal
            total_lista_decimal = Decimal(str(lista_compra.total_lista))
            subtotal_item_decimal = Decimal(str(item.subtotal)) # subtotal já deve ser Decimal pela property
            preco_unitario_item_decimal = Decimal(str(item.preco_unitario_no_momento))
            limite_calculado_decimal = Decimal(str(lista_compra.limite_compra_calculado))
            # --- FIM DAS CORREÇÕES PARA TypeError ---
            
            total_sem_este_item = total_lista_decimal - subtotal_item_decimal
            novo_subtotal_item = Decimal(nova_quantidade) * preco_unitario_item_decimal
            
            if (total_sem_este_item + novo_subtotal_item) > limite_calculado_decimal:
                messages.error(request, f"Não foi possível atualizar {item.produto.nome}. Limite de R$ {limite_calculado_decimal:.2f} seria excedido.")
            else:
                item.quantidade = nova_quantidade
                item.save()
                messages.success(request, f"Quantidade de {item.produto.nome} atualizada.")
        else:
            messages.error(request, "Erro ao atualizar item. Quantidade inválida ou dados incorretos.")
    return redirect('feira_app:minha_lista')


@login_required
@transaction.atomic
def remove_from_list_view(request, item_id):
    item = get_object_or_404(ItemDaLista, id=item_id)
    lista_compra = item.lista
    beneficiario_atual = get_beneficiario_atual(request.user)

    if not beneficiario_atual or lista_compra.beneficiario != beneficiario_atual:
        messages.error(request, "Acesso não autorizado.")
        return redirect('feira_app:minha_lista')

    if request.method == 'POST':
        produto_nome = item.produto.nome
        item.delete()
        messages.success(request, f"{produto_nome} removido da lista.")
    # Se for GET, ou após o POST, redireciona (evita re-submissão do form com refresh)
    return redirect('feira_app:minha_lista')
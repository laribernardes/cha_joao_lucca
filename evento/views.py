
from collections import Counter

from django.shortcuts import render, redirect
from django.db import transaction
from django.db.models import Count
from django.contrib import messages

from .models import Convidado, Acompanhante, Presente


# =========================================================
# PRESENTES PRINCIPAIS E LIMITES
# =========================================================

LIMITES_PRESENTES = {
    "RN": 10,
    "P": 20,
    "M": 30,
    "G": 30,
    "lenco": 30,
    "pomada": 10,
}

ITENS_PRINCIPAIS = list(LIMITES_PRESENTES.keys())

MIMOS_VALIDOS = [
    "macacao",
    "body",
    "mijao",
    "meia",
    "luvinha",
    "touca",
    "manta",
    "toalhinha_boca",
    "toalha_banho",
    "outros",
]


# =========================================================
# CONTAR PRESENTES JÁ ESCOLHIDOS
# =========================================================

def obter_disponibilidade():

    quantidades = {
        item: 0
        for item in ITENS_PRINCIPAIS
    }

    convidados = (
        Convidado.objects
        .filter(
            presenca=True,
            tamanho_fralda__in=ITENS_PRINCIPAIS
        )
        .values("tamanho_fralda")
        .annotate(total=Count("id"))
    )

    for registro in convidados:
        item = registro["tamanho_fralda"]
        quantidades[item] += registro["total"]

    acompanhantes = (
        Acompanhante.objects
        .filter(
            convidado__presenca=True,
            tipo="adulto",
            tamanho_fralda__in=ITENS_PRINCIPAIS
        )
        .values("tamanho_fralda")
        .annotate(total=Count("id"))
    )

    for registro in acompanhantes:
        item = registro["tamanho_fralda"]
        quantidades[item] += registro["total"]

    return {
        item: {
            "limite": limite,
            "escolhidos": quantidades[item],
            "restantes": max(
                0,
                limite - quantidades[item]
            ),
            "disponivel": quantidades[item] < limite,
        }
        for item, limite in LIMITES_PRESENTES.items()
    }


# =========================================================
# RENDERIZAR PÁGINA
# =========================================================

def renderizar_pagina(request, **contexto):

    contexto["disponibilidade"] = obter_disponibilidade()

    return render(
        request,
        "evento/index.html",
        contexto
    )


# =========================================================
# CONFIRMAÇÃO DE PRESENÇA
# =========================================================

def inicio(request):

    # =====================================================
    # ACESSO NORMAL À PÁGINA (GET)
    # =====================================================

    if request.method != "POST":

        # A mensagem de sucesso só aparece uma vez,
        # depois do redirecionamento.

        sucesso = any(
            mensagem.tags == "success"
            for mensagem in messages.get_messages(request)
        )

        return renderizar_pagina(
            request,
            sucesso=sucesso
        )

    # =====================================================
    # RECEBER DADOS DO FORMULÁRIO
    # =====================================================

    nome = request.POST.get(
        "nome", ""
    ).strip()

    presenca = request.POST.get(
        "presenca", ""
    ).strip()

    item_principal = request.POST.get(
        "tamanho_fralda", ""
    ).strip()

    mimo = request.POST.get(
        "mimo", ""
    ).strip()

    # =====================================================
    # VALIDAR CONVIDADO PRINCIPAL
    # =====================================================

    if not nome:
        return renderizar_pagina(
            request,
            erro="Digite seu nome para continuar."
        )

    if presenca not in ["sim", "nao"]:
        return renderizar_pagina(
            request,
            erro="Informe se você poderá estar presente."
        )

    confirmou_presenca = presenca == "sim"

    if (
        confirmou_presenca
        and item_principal not in ITENS_PRINCIPAIS
    ):
        return renderizar_pagina(
            request,
            erro=(
                "Escolha um item principal "
                "para confirmar sua presença."
            )
        )

    if mimo and mimo not in MIMOS_VALIDOS:
        return renderizar_pagina(
            request,
            erro="O mimo selecionado é inválido."
        )

    # =====================================================
    # VALIDAR ACOMPANHANTES
    # =====================================================

    acompanhantes_validos = []

    if confirmou_presenca:

        numero = 1

        while True:

            nome_acompanhante = request.POST.get(
                f"acompanhante_nome_{numero}", ""
            ).strip()

            tipo = request.POST.get(
                f"acompanhante_tipo_{numero}", ""
            ).strip()

            if not nome_acompanhante and not tipo:
                break

            if not nome_acompanhante:
                return renderizar_pagina(
                    request,
                    erro=(
                        "Informe o nome de "
                        "todos os acompanhantes."
                    )
                )

            if tipo not in ["adulto", "crianca"]:
                return renderizar_pagina(
                    request,
                    erro=(
                        f"Informe se {nome_acompanhante} "
                        "é adulto ou criança."
                    )
                )

            item_acompanhante = request.POST.get(
                f"acompanhante_fralda_{numero}", ""
            ).strip()

            mimo_acompanhante = request.POST.get(
                f"acompanhante_mimo_{numero}", ""
            ).strip()

            if (
                tipo == "adulto"
                and item_acompanhante not in ITENS_PRINCIPAIS
            ):
                return renderizar_pagina(
                    request,
                    erro=(
                        f"Escolha o item que "
                        f"{nome_acompanhante} irá levar."
                    )
                )

            if tipo == "crianca":
                item_acompanhante = ""

            if (
                mimo_acompanhante
                and mimo_acompanhante not in MIMOS_VALIDOS
            ):
                return renderizar_pagina(
                    request,
                    erro=(
                        f"O mimo escolhido para "
                        f"{nome_acompanhante} é inválido."
                    )
                )

            acompanhantes_validos.append({
                "nome": nome_acompanhante,
                "tipo": tipo,
                "item_principal": item_acompanhante,
                "mimo": mimo_acompanhante,
            })

            numero += 1

    # =====================================================
    # CONTAR PRESENTES DESTA CONFIRMAÇÃO
    # =====================================================

    itens_solicitados = Counter()

    if confirmou_presenca:

        itens_solicitados[item_principal] += 1

        for acompanhante in acompanhantes_validos:

            if acompanhante["tipo"] == "adulto":

                itens_solicitados[
                    acompanhante["item_principal"]
                ] += 1

    # =====================================================
    # VERIFICAR LIMITES E SALVAR
    # =====================================================

    with transaction.atomic():

        # Impede que duas confirmações reservem
        # o mesmo último presente simultaneamente.
        Presente.objects.select_for_update().get(
            nome="CONTROLE_CONFIRMACOES"
        )

        disponibilidade = obter_disponibilidade()

        for item, quantidade in itens_solicitados.items():

            if quantidade > disponibilidade[item]["restantes"]:

                nome_item = dict(
                    Convidado.ITEM_CHOICES
                ).get(item, item)

                return renderizar_pagina(
                    request,
                    erro=(
                        f"O presente {nome_item} não possui "
                        "mais quantidade suficiente. "
                        "Escolha outra opção."
                    )
                )

        # Salvar convidado principal.

        convidado = Convidado.objects.create(
            nome=nome,
            presenca=confirmou_presenca,
            tamanho_fralda=(
                item_principal
                if confirmou_presenca
                else ""
            ),
            mimo=(
                mimo
                if confirmou_presenca
                else ""
            ),
            acompanhantes=len(acompanhantes_validos),
        )

        # Salvar acompanhantes.

        for acompanhante in acompanhantes_validos:

            Acompanhante.objects.create(
                convidado=convidado,
                nome=acompanhante["nome"],
                tipo=acompanhante["tipo"],
                tamanho_fralda=acompanhante["item_principal"],
                mimo=acompanhante["mimo"],
            )

    # =====================================================
    # REDIRECIONAR APÓS SALVAR
    # =====================================================

    messages.success(
        request,
        "Confirmação registrada com sucesso."
    )

    # Redireciona para a mesma página usando GET.
    # Isso impede o reenvio do formulário ao atualizar.

    return redirect(request.path)

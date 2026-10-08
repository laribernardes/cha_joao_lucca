from django.contrib import admin
from django.db.models import Q

from .models import Convidado, Acompanhante, Presente


# =========================================================
# FILTRO DE ITENS PRINCIPAIS
# Convidado principal + acompanhantes adultos
# =========================================================

class FiltroItemPrincipal(admin.SimpleListFilter):
    title = "Item principal"
    parameter_name = "item_principal"

    def lookups(self, request, model_admin):
        return (
            ("RN", "Fralda RN"),
            ("P", "Fralda P"),
            ("M", "Fralda M"),
            ("G", "Fralda G"),
            ("lenco", "Lenço umedecido"),
            ("pomada", "Pomada"),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                Q(tamanho_fralda=self.value())
                |
                Q(
                    acompanhantes_detalhes__tipo="adulto",
                    acompanhantes_detalhes__tamanho_fralda=self.value()
                )
            ).distinct()

        return queryset


# =========================================================
# FILTRO DE MIMOS
# Convidado principal + acompanhantes
# =========================================================

class FiltroMimo(admin.SimpleListFilter):
    title = "Mimo"
    parameter_name = "mimo_evento"

    def lookups(self, request, model_admin):
        return (
            ("macacao", "Macacão"),
            ("body", "Body"),
            ("mijao", "Mijão"),
            ("meia", "Meia"),
            ("luvinha", "Luvinha"),
            ("touca", "Touca"),
            ("manta", "Manta"),
            ("toalhinha_boca", "Toalhinha de boca"),
            ("toalha_banho", "Toalha de banho"),
            ("outros", "Outros"),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                Q(mimo=self.value())
                |
                Q(acompanhantes_detalhes__mimo=self.value())
            ).distinct()

        return queryset


# =========================================================
# ADMIN DOS CONVIDADOS
# =========================================================

@admin.register(Convidado)
class ConvidadoAdmin(admin.ModelAdmin):

    change_list_template = "admin/evento/convidado/change_list.html"

    list_display = (
        "nome",
        "presenca",
        "item_principal",
        "mimo_escolhido",
        "adultos",
        "criancas",
        "total_pessoas",
        "data_confirmacao",
    )

    list_filter = (
        "presenca",
        FiltroItemPrincipal,
        FiltroMimo,
    )

    search_fields = (
        "nome",
        "acompanhantes_detalhes__nome",
    )

    # -----------------------------------------------------
    # ITEM PRINCIPAL DO CONVIDADO
    # -----------------------------------------------------

    @admin.display(description="Item principal")
    def item_principal(self, obj):
        if obj.tamanho_fralda:
            return obj.get_tamanho_fralda_display()

        return "—"

    # -----------------------------------------------------
    # MIMO DO CONVIDADO
    # -----------------------------------------------------

    @admin.display(description="Mimo")
    def mimo_escolhido(self, obj):
        if obj.mimo:
            return obj.get_mimo_display()

        return "—"

    # -----------------------------------------------------
    # ADULTOS
    # Convidado confirmado + acompanhantes adultos
    # -----------------------------------------------------

    @admin.display(description="Adultos")
    def adultos(self, obj):
        if not obj.presenca:
            return 0

        acompanhantes_adultos = (
            obj.acompanhantes_detalhes
            .filter(tipo="adulto")
            .count()
        )

        return 1 + acompanhantes_adultos

    # -----------------------------------------------------
    # CRIANÇAS
    # -----------------------------------------------------

    @admin.display(description="Crianças")
    def criancas(self, obj):
        if not obj.presenca:
            return 0

        return (
            obj.acompanhantes_detalhes
            .filter(tipo="crianca")
            .count()
        )

    # -----------------------------------------------------
    # TOTAL DA FAMÍLIA / CADASTRO
    # -----------------------------------------------------

    @admin.display(description="Total de pessoas")
    def total_pessoas(self, obj):
        if not obj.presenca:
            return 0

        return 1 + obj.acompanhantes_detalhes.count()

    # =====================================================
    # RESUMO GERAL DO EVENTO
    # =====================================================

    def changelist_view(self, request, extra_context=None):

        # -------------------------------------------------
        # PESSOAS
        # -------------------------------------------------

        convidados_confirmados = Convidado.objects.filter(
            presenca=True
        ).count()

        acompanhantes_adultos = Acompanhante.objects.filter(
            convidado__presenca=True,
            tipo="adulto"
        ).count()

        criancas = Acompanhante.objects.filter(
            convidado__presenca=True,
            tipo="crianca"
        ).count()

        total_adultos = (
            convidados_confirmados
            + acompanhantes_adultos
        )

        total_pessoas = (
            total_adultos
            + criancas
        )

        # -------------------------------------------------
        # ITENS PRINCIPAIS
        # -------------------------------------------------

        itens_principais = {
            "RN": 0,
            "P": 0,
            "M": 0,
            "G": 0,
            "lenco": 0,
            "pomada": 0,
        }

        for item in itens_principais:

            itens_convidados = Convidado.objects.filter(
                presenca=True,
                tamanho_fralda=item
            ).count()

            itens_acompanhantes = Acompanhante.objects.filter(
                convidado__presenca=True,
                tipo="adulto",
                tamanho_fralda=item
            ).count()

            itens_principais[item] = (
                itens_convidados
                + itens_acompanhantes
            )

        total_itens_principais = sum(
            itens_principais.values()
        )

        # -------------------------------------------------
        # MIMOS
        # -------------------------------------------------

        mimos = {
            "macacao": 0,
            "body": 0,
            "mijao": 0,
            "meia": 0,
            "luvinha": 0,
            "touca": 0,
            "manta": 0,
            "toalhinha_boca": 0,
            "toalha_banho": 0,
            "outros": 0,
        }

        for mimo in mimos:

            mimos_convidados = Convidado.objects.filter(
                presenca=True,
                mimo=mimo
            ).count()

            mimos_acompanhantes = Acompanhante.objects.filter(
                convidado__presenca=True,
                mimo=mimo
            ).count()

            mimos[mimo] = (
                mimos_convidados
                + mimos_acompanhantes
            )

        total_mimos = sum(mimos.values())

        # -------------------------------------------------
        # DADOS ENVIADOS PARA O TEMPLATE DO ADMIN
        # -------------------------------------------------

        extra_context = extra_context or {}

        extra_context.update({

            # Pessoas
            "total_adultos_evento": total_adultos,
            "total_criancas_evento": criancas,
            "total_pessoas_evento": total_pessoas,

            # Itens principais
            "fraldas_rn": itens_principais["RN"],
            "fraldas_p": itens_principais["P"],
            "fraldas_m": itens_principais["M"],
            "fraldas_g": itens_principais["G"],
            

            "itens_lenco": itens_principais["lenco"],
            "itens_pomada": itens_principais["pomada"],

            "total_itens_principais":
                total_itens_principais,

            # Mantemos esta variável temporariamente
            # para o template antigo não quebrar.
            "total_fraldas": (
                itens_principais["RN"]
                + itens_principais["P"]
                + itens_principais["M"]
                + itens_principais["G"]
                
            ),

            # Mimos
            "mimos_macacao": mimos["macacao"],
            "mimos_body": mimos["body"],
            "mimos_mijao": mimos["mijao"],
            "mimos_meia": mimos["meia"],
            "mimos_luvinha": mimos["luvinha"],
            "mimos_touca": mimos["touca"],
            "mimos_manta": mimos["manta"],
            "mimos_toalhinha_boca":
                mimos["toalhinha_boca"],
            "mimos_toalha_banho":
                mimos["toalha_banho"],
            "mimos_outros": mimos["outros"],

            "total_mimos": total_mimos,
        })

        return super().changelist_view(
            request,
            extra_context=extra_context
        )


# =========================================================
# ADMIN DOS ACOMPANHANTES
# =========================================================

@admin.register(Acompanhante)
class AcompanhanteAdmin(admin.ModelAdmin):

    list_display = (
        "nome",
        "tipo",
        "item_principal",
        "mimo_escolhido",
        "convidado",
    )

    list_filter = (
        "tipo",
        "tamanho_fralda",
        "mimo",
    )

    search_fields = (
        "nome",
        "convidado__nome",
    )

    @admin.display(description="Item principal")
    def item_principal(self, obj):
        if obj.tamanho_fralda:
            return obj.get_tamanho_fralda_display()

        return "—"

    @admin.display(description="Mimo")
    def mimo_escolhido(self, obj):
        if obj.mimo:
            return obj.get_mimo_display()

        return "—"


# =========================================================
# ADMIN DOS PRESENTES
# =========================================================

@admin.register(Presente)
class PresenteAdmin(admin.ModelAdmin):

    list_display = (
        "nome",
        "disponivel",
    )
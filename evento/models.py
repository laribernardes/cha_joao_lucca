
from django.db import models


class Presente(models.Model):
    nome = models.CharField(max_length=100)

    descricao = models.CharField(
        max_length=200,
        blank=True
    )

    disponivel = models.BooleanField(
        default=True
    )

    limite = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return self.nome


class Convidado(models.Model):

    ITEM_CHOICES = [
        ("RN", "Fralda RN"),
        ("P", "Fralda P"),
        ("M", "Fralda M"),
        ("G", "Fralda G"),
        ("lenco", "Lenço umedecido"),
        ("pomada", "Pomada"),
    ]

    MIMO_CHOICES = [
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
    ]

    nome = models.CharField(
        max_length=150
    )

    presenca = models.BooleanField(
        default=False
    )

    acompanhantes = models.PositiveIntegerField(
        default=0
    )

    # Mantemos o nome do campo para preservar
    # os dados já existentes no banco.
    tamanho_fralda = models.CharField(
        max_length=10,
        blank=True,
        choices=ITEM_CHOICES
    )

    presente = models.ForeignKey(
        Presente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    mimo = models.CharField(
        max_length=30,
        choices=MIMO_CHOICES,
        blank=True
    )

    data_confirmacao = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.nome


class Acompanhante(models.Model):

    TIPO_CHOICES = [
        ("adulto", "Adulto"),
        ("crianca", "Criança"),
    ]

    ITEM_CHOICES = [
        ("RN", "Fralda RN"),
        ("P", "Fralda P"),
        ("M", "Fralda M"),
        ("G", "Fralda G"),
        ("lenco", "Lenço umedecido"),
        ("pomada", "Pomada"),
    ]

    MIMO_CHOICES = [
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
    ]

    nome = models.CharField(
        max_length=150
    )

    convidado = models.ForeignKey(
        Convidado,
        on_delete=models.CASCADE,
        related_name="acompanhantes_detalhes"
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES
    )

    tamanho_fralda = models.CharField(
        max_length=10,
        choices=ITEM_CHOICES,
        blank=True
    )

    mimo = models.CharField(
        max_length=30,
        choices=MIMO_CHOICES,
        blank=True
    )

    def __str__(self):
        return f"{self.nome} - {self.get_tipo_display()}"

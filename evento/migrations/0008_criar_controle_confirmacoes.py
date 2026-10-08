from django.db import migrations


def criar_controle_confirmacoes(apps, schema_editor):
    Presente = apps.get_model("evento", "Presente")

    Presente.objects.using(schema_editor.connection.alias).get_or_create(
        nome="CONTROLE_CONFIRMACOES",
        defaults={
            "descricao": "Registro interno de controle das confirmações",
            "disponivel": False,
            "limite": 0,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("evento", "0007_presente_limite"),
    ]

    operations = [
        migrations.RunPython(
            criar_controle_confirmacoes,
            migrations.RunPython.noop,
        ),
    ]
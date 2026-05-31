# anki-deck-generator/apps/generator-app/src/generator_app/models.py
import genanki

def get_genanki_model(
    model_id: int,
    model_name: str,
    card_style: str,
    fields: list[str],
    qfmt: str,
    afmt: str,
    is_cloze: bool = True
) -> genanki.Model:
    """Erstellt ein voll-dynamisches genanki-Modell."""
    
    model_type = genanki.Model.CLOZE if is_cloze else None

    # Genanki erwartet eine Liste von Dictionaries für die Felder
    genanki_fields = [{"name": field} for field in fields]

    return genanki.Model(
        model_id,
        model_name,
        fields=genanki_fields,
        css=card_style,
        templates=[{
            "name": "Cloze Card Base Template",
            "qfmt": qfmt,
            "afmt": afmt,
        }],
        model_type=model_type
    )
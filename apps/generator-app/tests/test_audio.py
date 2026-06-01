from generator_app.services.audio import clean_cloze_text

def test_clean_cloze_text_standard():
    """Testet ob Standard-Lückentext richtig aufbereitet werden."""
    raw = "El libro es {{c1::rojo}}."
    assert clean_cloze_text(raw) == "El libro es rojo."

def test_clean_cloze_text_with_hint():
    """Testet, ob Anki-Hinweise/Tipps innerhalb der Klammern entfernt werden."""
    raw = "El {{c1::libro::Nomen}} es rojo."
    assert clean_cloze_text(raw) == "El libro es rojo."

def test_clean_cloze_text_multiple_clozes():
    """Testet, ob Sätze mit mehreren Lücken sauber verarbeitet werden."""
    raw = "{{c1::El}} libro es {{c2::rojo}}."
    assert clean_cloze_text(raw) == "El libro es rojo."

def test_clean_cloze_text_no_cloze():
    """Testet, ob ein Satz ohne Lücken unverändert bleibt."""
    raw = "Carlos lee un libro."
    assert clean_cloze_text(raw) == "Carlos lee un libro."
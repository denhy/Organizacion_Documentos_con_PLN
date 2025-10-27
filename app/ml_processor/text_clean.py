# -*- coding: utf-8 -*-
import re
import unicodedata

# Tu lista de stopwords:
STOP_ES = {
    "de","es","la","que","el","en","y","a","los","del","se","las","por","un","para","con","no","una",
    "su","al","lo","como","más","pero","sus","le","ya","o","este","sí","porque","esta","entre","cuando",
    "muy","sin","sobre","también","me","hasta","hay","donde","quien","desde","todo","nos","durante","todos",
    "uno","les","ni","contra","otros","ese","eso","ante","ellos","e","esto","mí","antes","algunos","qué",
    "unos","yo","otro","otras","otra","él","tanto","esa","estos","mucho","quienes","nada","muchos","cual",
    "poco","ella","estar","estas","algunas","algo","nosotros","mi","mis","tú","te","ti","tu","tus","ellas",
    "nosotras","mío","mía","míos","mías","tuyo","tuya","tuyos","tuyas","suyo","suya","suyos","suyas",
    "nuestro","nuestra","nuestros","nuestras","vuestro","vuestra","vuestros","vuestras","esos","esas",
    "estoy","estás","está","estamos","estáis","están","esté","estés","estemos","estaré","estarás","estará",
    "estaremos","estaréis","estarán","estaría","estarías","estaba","estabas","estábamos","estabais","estaban",
    "estuve","son","cada","puede","fue","estuviste","estuvo","estuvimos","estuvieron","estuviera","estuvieras",
    "estuviéramos","así","estuvieran","además","si","tienen","tiene","cómo","así","ha","según","segun",
    "mientras","debido","dijo","manera","ello","mejor","través","tenemos","fue","año","han","caso","empresas"
}

_URL_RE  = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_MAIL_RE = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b")
_NUM_RE  = re.compile(r"\b\d+([\.,]\d+)*\b")
_WS_RE   = re.compile(r"\s+")

def _strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", s)
        if not unicodedata.combining(c)
    )

def clean_text_es(text: str,
                  stopset=STOP_ES,
                  remove_numbers: bool = True,
                  min_token_len: int = 2) -> str:
    """Limpia texto en español para embeddings/clustering/clasificación."""
    if not isinstance(text, str):
        return ""

    # 1) normaliza y minúsculas
    t = text.replace("\u00A0", " ").strip().lower()

    # 2) elimina urls, emails
    t = _URL_RE.sub(" ", t)
    t = _MAIL_RE.sub(" ", t)

    # 3) quita acentos (opcional, ayuda a unificar vocabulario)
    t = _strip_accents(t)

    # 4) sustituye signos/puntuación por espacio
    t = re.sub(r"[^\w\s]", " ", t)

    # 5) números (opcional)
    if remove_numbers:
        t = _NUM_RE.sub(" ", t)

    # 6) colapsa espacios
    t = _WS_RE.sub(" ", t).strip()

    # 7) filtra stopwords y tokens muy cortos
    tokens = [w for w in t.split() if len(w) >= min_token_len and w not in stopset]

    return " ".join(tokens)

def clean_texts_es(texts, **kwargs):
    """Version batch. Devuelve lista del mismo largo."""
    return [clean_text_es(t, **kwargs) for t in texts]

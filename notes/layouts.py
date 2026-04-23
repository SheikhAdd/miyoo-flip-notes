from __future__ import annotations

from .models import KeyboardLayout, LayoutFamily


LAYOUT_LIBRARY: dict[str, KeyboardLayout] = {
    "en_qwerty": KeyboardLayout(
        layout_id="en_qwerty",
        title="English QWERTY",
        short="EN",
        family=LayoutFamily.ALPHA,
        rows=[
            list("qwertyuiop"),
            list("asdfghjkl"),
            ["SHIFT", *list("zxcvbnm"), "BACK"],
            ["LANG", "SYM", "SPACE", "LEFT", "RIGHT"],
            [".", ",", "-", "'", "ENTER"],
        ],
    ),
    "ru_jcuken": KeyboardLayout(
        layout_id="ru_jcuken",
        title="Russian JCUKEN",
        short="RU",
        family=LayoutFamily.ALPHA,
        rows=[
            list("йцукенгшщзх"),
            list("фывапролджэ"),
            ["SHIFT", *list("ячсмитьбю"), "BACK"],
            ["LANG", "SYM", "SPACE", "LEFT", "RIGHT"],
            [".", ",", "-", "'", "ENTER"],
        ],
    ),
    "kz_cyrillic": KeyboardLayout(
        layout_id="kz_cyrillic",
        title="Kazakh Cyrillic",
        short="KZ",
        family=LayoutFamily.ALPHA,
        rows=[
            list("әіңғүұқөһ"),
            list("йцукенгшщз"),
            ["SHIFT", *list("фывапролд"), "BACK"],
            ["я", "ч", "с", "м", "и", "т", "ь", "б", "ю"],
            ["LANG", "SYM", "SPACE", "LEFT", "RIGHT", "ENTER"],
        ],
    ),
    "de_qwertz": KeyboardLayout(
        layout_id="de_qwertz",
        title="German QWERTZ",
        short="DE",
        family=LayoutFamily.ALPHA,
        rows=[
            list("qwertzuiop"),
            list("asdfghjklö"),
            ["SHIFT", *list("yxcvbnmüä"), "BACK"],
            ["LANG", "SYM", "SPACE", "LEFT", "RIGHT"],
            [".", ",", "-", "ß", "ENTER"],
        ],
    ),
    "fr_azerty": KeyboardLayout(
        layout_id="fr_azerty",
        title="French AZERTY",
        short="FR",
        family=LayoutFamily.ALPHA,
        rows=[
            list("azertyuiop"),
            list("qsdfghjklm"),
            ["SHIFT", *list("wxcvbnéèà"), "BACK"],
            ["LANG", "SYM", "SPACE", "LEFT", "RIGHT"],
            [".", ",", "-", "'", "ENTER"],
        ],
    ),
    "es_qwerty": KeyboardLayout(
        layout_id="es_qwerty",
        title="Spanish QWERTY",
        short="ES",
        family=LayoutFamily.ALPHA,
        rows=[
            list("qwertyuiop"),
            list("asdfghjklñ"),
            ["SHIFT", *list("zxcvbnmáé"), "BACK"],
            ["LANG", "SYM", "SPACE", "LEFT", "RIGHT"],
            [".", ",", "-", "¿", "ENTER"],
        ],
    ),
    "tr_q": KeyboardLayout(
        layout_id="tr_q",
        title="Turkish Q",
        short="TR",
        family=LayoutFamily.ALPHA,
        rows=[
            list("qwertyuıop"),
            list("asdfghjklş"),
            ["SHIFT", *list("zxcvbnmöç"), "BACK"],
            ["LANG", "SYM", "SPACE", "LEFT", "RIGHT"],
            [".", ",", "-", "ğ", "ENTER"],
        ],
    ),
    "symbols_basic": KeyboardLayout(
        layout_id="symbols_basic",
        title="Symbols",
        short="SYM",
        family=LayoutFamily.SYMBOLS,
        rows=[
            list("1234567890"),
            ["@", "#", "&", "*", "(", ")", "[", "]", "{", "}"],
            [".", ",", "?", "!", "+", "-", "_", "/", "BACK"],
            ["ABC", "SPACE", "LEFT", "RIGHT", "ENTER"],
            ["'", '"', ";", ":", "="],
        ],
    ),
}

LAYOUT_ORDER = list(LAYOUT_LIBRARY)
DEFAULT_LAYOUT_IDS = ["en_qwerty", "ru_jcuken", "kz_cyrillic", "symbols_basic"]


def get_layout(layout_id: str) -> KeyboardLayout:
    return LAYOUT_LIBRARY[layout_id]


def normalized_active_layouts(layout_ids: list[str]) -> list[str]:
    valid = [layout_id for layout_id in layout_ids if layout_id in LAYOUT_LIBRARY]
    if not valid:
        return list(DEFAULT_LAYOUT_IDS)

    ordered: list[str] = []
    for layout_id in LAYOUT_ORDER:
        if layout_id in valid and layout_id not in ordered:
            ordered.append(layout_id)
    return ordered


def alpha_layout_ids(layout_ids: list[str]) -> list[str]:
    return [layout_id for layout_id in normalized_active_layouts(layout_ids) if get_layout(layout_id).family == LayoutFamily.ALPHA]

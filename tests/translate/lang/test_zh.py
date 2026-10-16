import pytest

from translate.lang import factory


def test_punctranslate() -> None:
    """Tests that we can translate punctuation."""
    language = factory.getlanguage("zh")
    assert language.punctranslate("") == ""
    assert language.punctranslate("abc efg") == "abc efg"
    assert language.punctranslate("abc efg.") == "abc efg。"
    assert language.punctranslate("(abc efg).") == "(abc efg)。"
    assert language.punctranslate("(abc efg). hijk") == "(abc efg)。hijk"
    assert language.punctranslate(".") == "。"
    assert language.punctranslate("abc efg...") == "abc efg..."


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("第一行?\n第二行.", "第一行？\n第二行。"),
        ("First?\n\nSecond.", "First？\n\nSecond。"),
        ("First?\nSecond?\n", "First？\nSecond？\n"),
        ("Hello!\nQuestion?\nEnd.", "Hello！\nQuestion？\nEnd。"),
        ("First? Second.", "First？Second。"),
        ("First!\nSecond.", "First！\nSecond。"),
    ],
)
def test_punctranslate_preserves_newlines(text: str, expected: str) -> None:
    language = factory.getlanguage("zh")
    assert language.punctranslate(text) == expected


def test_sentences() -> None:
    """Tests basic functionality of sentence segmentation."""
    language = factory.getlanguage("zh")
    sentences = language.sentences("")
    assert sentences == []

    sentences = language.sentences(
        "這個用戶名稱已經存在。現在會寄一封信給已登記的電郵地址。\n"
    )
    assert sentences == ["這個用戶名稱已經存在。", "現在會寄一封信給已登記的電郵地址。"]

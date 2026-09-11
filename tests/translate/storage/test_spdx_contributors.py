# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

# REUSE-IgnoreStart
from io import BytesIO
from unittest.mock import patch

import pytest

from translate.storage.pypo import pofile


def parse_header(comments: str) -> pofile:
    return pofile(
        BytesIO((comments + '\nmsgid ""\nmsgstr "MIME-Version: 1.0\\n"\n').encode())
    )


def update(store: pofile, name="Jane", email="jane@example.com", year="2026"):
    with patch("translate.storage.poheader.time.strftime", return_value=year):
        store.updatecontributor(name, email, spdx=True)
    return store.header().getnotes("translator")


def test_convert_and_preserve_comments():
    store = parse_header(
        "# Project translation.\n"
        "# Copyright (C) 2020 Project authors\n"
        "# SPDX-License-Identifier: GPL-3.0-or-later\n"
        "#\n"
        "# Translators:\n"
        "# Jane <jane@example.com>, 2020, 2024.\n"
        "# Čeněk, 2022-2023.\n"
        "#\n"
        "# Please report problems upstream."
    )
    store.header().addnote("An extracted note", "developer")
    assert update(store) == (
        "Project translation.\n"
        "Copyright (C) 2020 Project authors\n"
        "SPDX-License-Identifier: GPL-3.0-or-later\n"
        "\n"
        "Translators:\n"
        "SPDX-FileCopyrightText: 2020, 2024, 2026 Jane <jane@example.com>\n"
        "SPDX-FileCopyrightText: 2022-2023 Čeněk\n"
        "\n"
        "Please report problems upstream."
    )
    assert store.header().getnotes("developer") == "An extracted note"
    first = bytes(store)
    update(store)
    assert bytes(store) == first
    assert "2020, 2024, 2026, 2027 Jane" in update(store, year="2027")


def test_mixed_headers_and_exact_identity():
    store = parse_header(
        "# Jane <jane@example.com>, 2020.\n"
        "# SPDX-FileCopyrightText: 2024 Jane <jane@example.com>\n"
        "# Mary Jane <jane@example.com>, 2023.\n"
        "# Jane <other@example.com>, 2022.\n"
        "# Jane, 2021."
    )
    result = update(store)
    assert result.count("SPDX-FileCopyrightText:") == 4
    assert "2020, 2024, 2026 Jane <jane@example.com>" in result
    assert "2023 Mary Jane <jane@example.com>" in result
    assert "2022 Jane <other@example.com>" in result
    assert "2021 Jane" in result.splitlines()[-1]


@pytest.mark.parametrize("years", ["2026", "2024-2027", "2024–2027", "2020, 2024-2027"])
def test_existing_year(years):
    store = parse_header(f"# SPDX-FileCopyrightText: {years} Jane <jane@example.com>")
    before = bytes(store)
    update(store)
    assert bytes(store) == before


def test_missing_email_and_placeholder():
    store = parse_header(
        "# Project\n# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.\n#\n# Notice"
    )
    result = update(store, name="Čeněk", email=None)
    assert result == "Project\nSPDX-FileCopyrightText: 2026 Čeněk\n\nNotice"
    assert update(store, name="Čeněk", email=None) == result


@pytest.mark.parametrize(
    "notice",
    [
        "SPDX-FileCopyrightText: Project authors",
        "SPDX-FileCopyrightText: 2027-2020 Jane <jane@example.com>",
        "Copyright Jane <jane@example.com>, 2020.",
        "Jane <jane@example.com>, YEAR.",
    ],
)
def test_unrecognized_claim_preserved(notice):
    store = parse_header(f"# {notice}")
    assert notice in update(store)


def test_no_header():
    store = pofile(noheader=True)
    store.updatecontributor("Jane", spdx=True)
    assert store.header() is None


def test_default_unchanged():
    store = parse_header("# Jane <jane@example.com>, 2020.")
    with patch("translate.storage.poheader.time.strftime", return_value="2026"):
        store.updatecontributor("Jane", "jane@example.com")
    assert (
        store.header().getnotes("translator") == "Jane <jane@example.com>, 2020, 2026."
    )


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
def test_preserve_newlines(newline: str) -> None:
    comments = [
        "# Translation notices.",
        "# Jane <jane@example.com>, 2024.",
        "# John <john@example.com>, 2023.",
        "#",
        "# A retained notice with a Unicode separator: \u2028.",
    ]
    source = newline.join([*comments, 'msgid ""', 'msgstr "MIME-Version: 1.0\\n"', ""])
    store = pofile(BytesIO(source.encode()))
    assert store.header().getnotes("translator") == newline.join(
        comment.removeprefix("#").removeprefix(" ") for comment in comments
    )
    update(store)
    expected_comments = [
        comments[0],
        "# SPDX-FileCopyrightText: 2024, 2026 Jane <jane@example.com>",
        "# SPDX-FileCopyrightText: 2023 John <john@example.com>",
        *comments[3:],
    ]
    output = bytes(store)
    assert (
        output.split(b'msgid ""')[0]
        == (newline.join(expected_comments) + newline).encode()
    )
    reparsed = pofile(BytesIO(output))
    assert reparsed.header().getnotes("translator") == store.header().getnotes(
        "translator"
    )
    update(reparsed)
    assert bytes(reparsed) == output


@pytest.mark.parametrize("position", ["before", "after"])
def test_dated_prose_preserved(position: str) -> None:
    notice = "# Do not edit manually, 2024."
    author = "# Jane <jane@example.com>, 2024."
    comments = [notice, author] if position == "before" else [author, notice]
    store = parse_header("\n".join(comments))
    result = update(store)
    assert "Do not edit manually, 2024." in result.splitlines()
    assert result.count("SPDX-FileCopyrightText:") == 1


@pytest.mark.parametrize("heading", ["Translators:", "Contributors:"])
@pytest.mark.parametrize("separator", ["", "This file uses UTF-8."])
def test_email_less_contributor_context(heading: str, separator: str) -> None:
    store = parse_header(
        f"# {heading}\n# Čeněk, 2022-2023.\n# {separator}\n# Do not edit manually, 2024."
    )
    result = update(store)
    assert "SPDX-FileCopyrightText: 2022-2023 Čeněk" in result
    assert "Do not edit manually, 2024." in result.splitlines()


def test_unrelated_email_less_entry_preserved() -> None:
    store = parse_header("# Historical note, 2024.")
    assert "Historical note, 2024." in update(store).splitlines()


def test_current_email_less_contributor_recognized() -> None:
    store = parse_header("# Jane, 2024.")
    assert update(store, email=None) == "SPDX-FileCopyrightText: 2024, 2026 Jane"


@pytest.mark.parametrize(
    "entry",
    [
        "Jane <jane@example.com>, 2024.",
        "SPDX-FileCopyrightText: 2024 Jane <jane@example.com>",
    ],
)
def test_omitted_email_matches_unique_name(entry: str) -> None:
    store = parse_header(f"# {entry}\n# Mary Jane <mary@example.com>, 2023.")
    result = update(store, email=None)
    assert result.count("SPDX-FileCopyrightText:") == 2
    assert "SPDX-FileCopyrightText: 2024, 2026 Jane <jane@example.com>" in result
    assert "SPDX-FileCopyrightText: 2023 Mary Jane <mary@example.com>" in result
    assert update(store, email=None) == result


def test_omitted_email_does_not_merge_ambiguous_names() -> None:
    store = parse_header(
        "# Jane <jane@example.com>, 2024.\n# Jane <other@example.com>, 2023."
    )
    result = update(store, email=None)
    assert result.splitlines() == [
        "SPDX-FileCopyrightText: 2024 Jane <jane@example.com>",
        "SPDX-FileCopyrightText: 2023 Jane <other@example.com>",
        "SPDX-FileCopyrightText: 2026 Jane",
    ]
    assert update(store, email=None) == result


def test_omitted_email_prefers_existing_email_less_identity() -> None:
    store = parse_header("# Jane, 2020.\n# Jane <jane@example.com>, 2024.")
    assert update(store, email=None).splitlines() == [
        "SPDX-FileCopyrightText: 2020, 2026 Jane",
        "SPDX-FileCopyrightText: 2024 Jane <jane@example.com>",
    ]


# REUSE-IgnoreEnd

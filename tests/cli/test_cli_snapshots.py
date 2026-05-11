from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CASE_DATA_DIR = Path(__file__).with_name("data")
VERSION_RE = re.compile(r'"Translate Toolkit [^"]+"')
PO_METADATA_RE = re.compile(
    r'^"(?P<field>POT-Creation-Date|X-Generator): .*?\\n"$',
    re.MULTILINE,
)
RELATIVE_PATH_RE = re.compile(r"\.(?:/|\\)(?:data|results)(?:/|\\)[^\s'\"<>]+")


@dataclass(frozen=True, slots=True)
class CliCase:
    name: str
    script: str
    args: tuple[str, ...]
    outputs: tuple[str, ...] = ()
    normalize_version: bool = False


CASES = (
    CliCase(
        "test_flatxml2po",
        "flatxml2po",
        ("--progress=none", "{data}/one.xml", "{result}/out.po"),
        ("out.po",),
    ),
    CliCase(
        "test_flatxml2po_wrongkey",
        "flatxml2po",
        ("--progress=none", "{data}/one.xml", "{result}/out.txt", "--key", "wrong"),
        ("out.txt",),
    ),
    CliCase(
        "test_flatxml2po_wrongns",
        "flatxml2po",
        (
            "--progress=none",
            "{data}/one.xml",
            "{result}/out.txt",
            "--namespace",
            "wrong",
        ),
        ("out.txt",),
    ),
    CliCase(
        "test_flatxml2po_wrongroot",
        "flatxml2po",
        ("--progress=none", "{data}/one.xml", "{result}/out.txt", "--root", "wrong"),
        ("out.txt",),
    ),
    CliCase(
        "test_flatxml2po_wrongvalue",
        "flatxml2po",
        ("--progress=none", "{data}/one.xml", "{result}/out.txt", "--value", "wrong"),
        ("out.txt",),
    ),
    CliCase(
        "test_junitmsgfmt_failure",
        "junitmsgfmt",
        ("{data}/one.po",),
    ),
    CliCase(
        "test_junitmsgfmt_untranslated",
        "junitmsgfmt",
        ("--untranslated", "{data}/one.po"),
    ),
    CliCase(
        "test_po2csv",
        "po2csv",
        ("--progress=none", "{data}/one.po", "{result}/out.txt"),
        ("out.txt",),
    ),
    CliCase(
        "test_po2flatxml",
        "po2flatxml",
        ("--progress=none", "{data}/one.po", "{result}/out.xml"),
        ("out.xml",),
    ),
    CliCase(
        "test_po2flatxml_params",
        "po2flatxml",
        (
            "--progress=none",
            "{data}/one.po",
            "{result}/out.xml",
            "--root",
            "dictionary",
            "--value",
            "translation",
            "--key",
            "resource",
            "--namespace",
            "urn:translate-toolkit:flatxml-test-suite",
            "--indent",
            "8",
        ),
        ("out.xml",),
    ),
    CliCase(
        "test_po2flatxml_preserve",
        "po2flatxml",
        (
            "--progress=none",
            "-i",
            "{data}/one.po",
            "-t",
            "{data}/two.xml",
            "-o",
            "{result}/out.xml",
        ),
        ("out.xml",),
    ),
    CliCase(
        "test_po2flatxml_template",
        "po2flatxml",
        (
            "--progress=none",
            "-i",
            "{data}/one.po",
            "-t",
            "{data}/two.xml",
            "-o",
            "{result}/out.xml",
            "--root",
            "dictionary",
            "--value",
            "translation",
            "--key",
            "resource",
            "--namespace",
            "urn:translate-toolkit:flatxml-test-suite",
            "--indent",
            "4",
        ),
        ("out.xml",),
    ),
    CliCase(
        "test_po2html",
        "po2html",
        (
            "--progress=none",
            "-t",
            "{data}/template.html",
            "{data}/one.po",
            "{result}/out.txt",
        ),
        ("out.txt",),
    ),
    CliCase(
        "test_po2json_files_removeuntranslated",
        "po2json",
        (
            "--removeuntranslated",
            "--progress=none",
            "-t",
            "{data}/template.json",
            "{data}/translations.po",
            "{result}/out.json",
        ),
        ("out.json",),
    ),
    CliCase(
        "test_po2prop_mozilla_files",
        "po2prop",
        (
            "--personality=mozilla",
            "--progress=none",
            "-t",
            "{data}/template.properties",
            "{data}/translations.po",
            "{result}/out.properties",
        ),
        ("out.properties",),
    ),
    CliCase(
        "test_po2ts",
        "po2ts",
        ("--progress=none", "{data}/one.po", "{result}/out.txt"),
        ("out.txt",),
    ),
    CliCase(
        "test_po2txt",
        "po2txt",
        ("--progress=none", "{data}/one.po", "{result}/out.txt"),
        ("out.txt",),
    ),
    CliCase(
        "test_po2txt_threshold",
        "po2txt",
        ("--progress=none", "--threshold=100", "{data}/one.po", "{result}/out.txt"),
        ("out.txt",),
    ),
    CliCase(
        "test_pofilter_listfilters",
        "pofilter",
        ("--listfilters",),
    ),
    CliCase(
        "test_pofilter_manpage",
        "pofilter",
        ("--manpage",),
        normalize_version=True,
    ),
    CliCase(
        "test_posegment",
        "posegment",
        ("--progress=none", "{data}/one.po", "{result}/out.po"),
        ("out.po",),
    ),
    CliCase(
        "test_poswap_comments",
        "poswap",
        ("--progress=none", "-t", "{data}/af.po", "{data}/fr.po", "{result}/out.po"),
        ("out.po",),
    ),
    CliCase(
        "test_poswap_fr_af",
        "poswap",
        ("--progress=none", "-t", "{data}/af.po", "{data}/fr.po", "{result}/out.po"),
        ("out.po",),
    ),
    CliCase(
        "test_poswap_fr_af_reverse",
        "poswap",
        (
            "--progress=none",
            "--reverse",
            "-t",
            "{data}/fr_af.po",
            "{data}/fr.po",
            "{result}/out.po",
        ),
        ("out.po",),
    ),
    CliCase(
        "test_poswap_intermediate",
        "poswap",
        (
            "--progress=none",
            "--intermediate",
            "-t",
            "{data}/en.po",
            "{data}/es.po",
            "{result}/out.po",
        ),
        ("out.po",),
    ),
    CliCase(
        "test_poswap_intermediate_partial",
        "poswap",
        (
            "--progress=none",
            "--intermediate",
            "-t",
            "{data}/en.po",
            "{data}/es.po",
            "{result}/out.po",
        ),
        ("out.po",),
    ),
    CliCase(
        "test_poswap_missing_units",
        "poswap",
        ("--progress=none", "-t", "{data}/af.po", "{data}/fr.po", "{result}/out.po"),
        ("out.po",),
    ),
    CliCase(
        "test_prop2po",
        "prop2po",
        (),
    ),
    CliCase(
        "test_prop2po_dirs",
        "prop2po",
        ("{data}/one", "{result}/out"),
        ("out",),
    ),
    CliCase(
        "test_prop2po_files",
        "prop2po",
        ("--progress=none", "{data}/one.properties", "{result}/out.po"),
        ("out.po",),
    ),
    CliCase(
        "test_prop2po_files_templates",
        "prop2po",
        (
            "--progress=none",
            "-t",
            "{data}/one.properties",
            "{data}/two.properties",
            "{result}/out.po",
        ),
        ("out.po",),
    ),
    CliCase(
        "test_rc2po",
        "rc2po",
        ("--progress=none", "-i", "{data}/one.rc", "-o", "{result}/out.po"),
        ("out.po",),
    ),
)


def _copy_case_inputs(case: CliCase, workdir: Path) -> None:
    def ignore_expected_outputs(_directory: str, names: list[str]) -> set[str]:
        return {
            name
            for name in names
            if name in {"stdout.txt", "stderr.txt", "out"} or name.startswith("out.")
        }

    source_dir = CASE_DATA_DIR / case.name
    target_dir = workdir / "data" / case.name
    if source_dir.exists():
        shutil.copytree(source_dir, target_dir, ignore=ignore_expected_outputs)
    else:
        target_dir.mkdir(parents=True)


def _render_args(case: CliCase) -> list[str]:
    return [
        arg.format(data=f"./data/{case.name}", result=f"./results/{case.name}")
        for arg in case.args
    ]


def _env() -> dict[str, str]:
    env = os.environ.copy()
    python_path = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{REPO_ROOT}{os.pathsep}{python_path}" if python_path else str(REPO_ROOT)
    )
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _read_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


def _normalize(text: str, workdir: Path, case: CliCase) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "")
    normalized = normalized.replace(workdir.as_posix(), ".")
    normalized = normalized.replace(str(workdir), ".")
    normalized = RELATIVE_PATH_RE.sub(
        lambda match: match.group(0).replace("\\", "/"),
        normalized,
    )
    normalized = re.sub(
        rf"{re.escape(case.script)}\.exe",
        case.script,
        normalized,
        flags=re.IGNORECASE,
    )
    normalized = PO_METADATA_RE.sub(
        lambda match: f'"{match.group("field")}: @{match.group("field").upper()}@\\n"',
        normalized,
    )
    if case.normalize_version:
        normalized = VERSION_RE.sub('"Translate Toolkit @VERSION@"', normalized)
    return normalized


def _collect_outputs(
    case: CliCase, result_dir: Path, workdir: Path
) -> dict[str, str | None]:
    output_files: dict[str, str | None] = {}
    for output in case.outputs:
        path = result_dir / output
        if path.is_dir():
            for child in sorted(item for item in path.rglob("*") if item.is_file()):
                output_files[child.relative_to(result_dir).as_posix()] = _normalize(
                    _read_text(child), workdir, case
                )
        elif path.exists():
            output_files[output] = _normalize(_read_text(path), workdir, case)
        else:
            output_files[output] = None
    return output_files


def _script_path(case: CliCase) -> str:
    script = shutil.which(case.script)
    if script is None:
        pytest.fail(f"Could not find {case.script!r} on PATH")
    return script


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_cli_case(case: CliCase, tmp_path: Path, snapshot) -> None:
    workdir = tmp_path / "cli"
    result_dir = workdir / "results" / case.name
    result_dir.mkdir(parents=True)
    _copy_case_inputs(case, workdir)

    result = subprocess.run(
        [_script_path(case), *_render_args(case)],
        cwd=workdir,
        env=_env(),
        capture_output=True,
        check=False,
    )

    assert {
        "returncode": result.returncode,
        "stdout": _normalize(result.stdout.decode("utf-8"), workdir, case),
        "stderr": _normalize(result.stderr.decode("utf-8"), workdir, case),
        "outputs": _collect_outputs(case, result_dir, workdir),
    } == snapshot

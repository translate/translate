from __future__ import annotations

import subprocess
from argparse import ArgumentParser
from os.path import basename
from time import time
from typing import Iterable, NamedTuple

import lxml.etree as etree


class MsgfmtTester:
    def __init__(self, files: Iterable[str], untranslated=False):
        self._detect_untranslated = untranslated
        self._files = files

    def run(self):
        results = list(map(self._run_msgfmt, self._files))
        self._print_results(results)

    def _run_msgfmt(self, pofile: str):
        start_time = time()
        process = subprocess.Popen(
            ["msgfmt", "-cv", "-o", "/dev/null", pofile],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate()
        stderr = stderr.replace(pofile, basename(pofile))

        failures: list[CheckFailure] = []
        if process.returncode:
            failures.append(CheckFailure(stderr, "Failure"))
        elif self._detect_untranslated and "untranslated" in stderr:
            failures.append(CheckFailure(stderr, "Untranslated messages"))
        return CheckResult(
            pofile,
            0 if "test_junitmsgfmt" in pofile else time() - start_time,
            failures,
        )

    @staticmethod
    def _print_results(results: list[CheckResult]):
        failures = len([r for r in results if len(r.failures)])
        total_time = sum([r.time for r in results], 0)
        root = etree.Element(
            "testsuite",
            name="msgfmt",
            errors="0",
            skips="0",
            failures=str(failures),
            tests=str(len(results)),
            time=f"{total_time:.4f}",
        )
        for result in results:
            case = etree.SubElement(
                root,
                "testcase",
                classname="msgfmt",
                name=f"check[{result.file}]",
                file=result.file,
                time=f"{result.time:.4f}",
            )
            for failure in result.failures:
                etree.SubElement(
                    case, "failure", message=failure.message
                ).text = failure.text
        print(etree.tostring(root, encoding="unicode", pretty_print=True))


class CheckResult(NamedTuple):
    file: str
    time: float
    failures: list[CheckFailure]


class CheckFailure(NamedTuple):
    text: str
    message: str


def main(arguments=None):
    parser = ArgumentParser()
    parser.add_argument(
        "--untranslated",
        action="store_true",
        default=False,
        help="fail on untranslated messages",
    )
    parser.add_argument("files", nargs="+")

    args = parser.parse_args(arguments)

    MsgfmtTester(args.files, untranslated=args.untranslated).run()


if __name__ == "__main__":
    main()

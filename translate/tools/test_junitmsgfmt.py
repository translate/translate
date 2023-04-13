from pytest import mark, param

from translate.tools import junitmsgfmt

from ._test_utils import requires_py38_mark


@requires_py38_mark
@mark.parametrize(
    "opts",
    [
        param(["tests/cli/data/test_junitmsgfmt_failure/one.po"], id="failure"),
        param(
            ["--untranslated", "tests/cli/data/test_junitmsgfmt_untranslated/one.po"],
            id="untranslated",
        ),
    ],
)
def test_output(opts, capsys, snapshot):
    junitmsgfmt.main([*opts])
    stdout = capsys.readouterr()[0]

    assert stdout == snapshot

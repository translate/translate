import logging
import optparse
import os
import sys
from io import BytesIO, StringIO
from tempfile import NamedTemporaryFile
from types import SimpleNamespace

import pytest

from translate.misc import optrecurse


def _noop_processor(inputfile, outputfile, templatefile):
    return True


def _make_exc_info(exc):
    """Create an exc_info tuple for testing warning methods."""
    result = None
    try:
        raise exc
    except type(exc):
        result = sys.exc_info()
    return result


class TestRecursiveOptionParser:
    def test_splitext(self) -> None:
        """Test the ``optrecurse.splitext`` function."""
        self.parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        name = "name"
        extension = "ext"
        filename = name + os.extsep + extension
        dirname = os.path.join("some", "path", "to")
        fullpath = os.path.join(dirname, filename)
        root = os.path.join(dirname, name)
        print(fullpath)
        assert self.parser.splitext(fullpath) == (root, extension)

    def test_outputfile_receives_bytes(self, capsys) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})

        temp_file = NamedTemporaryFile(delete=False)
        temp_file.close()
        try:
            out = parser.openoutputfile(None, temp_file.name)
            out.write(b"binary stuff")
            out.close()
        finally:
            os.unlink(temp_file.name)

        out = parser.openoutputfile(None, None)  # To sys.stdout
        out.write(b"binary stuff")


class TestIsRecursive:
    """Tests for RecursiveOptionParser.isrecursive."""

    def test_none_is_not_recursive(self) -> None:
        assert optrecurse.RecursiveOptionParser.isrecursive(None) is False

    def test_list_is_recursive(self) -> None:
        assert optrecurse.RecursiveOptionParser.isrecursive(["a", "b"]) is True

    def test_empty_list_is_recursive(self) -> None:
        assert optrecurse.RecursiveOptionParser.isrecursive([]) is True

    def test_directory_is_recursive(self, tmp_path) -> None:
        assert optrecurse.RecursiveOptionParser.isrecursive(str(tmp_path)) is True

    def test_file_is_not_recursive(self, tmp_path) -> None:
        f = tmp_path / "file.txt"
        f.write_text("content")
        assert optrecurse.RecursiveOptionParser.isrecursive(str(f)) is False

    def test_nonexistent_path_is_not_recursive(self) -> None:
        assert (
            optrecurse.RecursiveOptionParser.isrecursive("/nonexistent/path") is False
        )


class TestIsExcluded:
    """Tests for RecursiveOptionParser.isexcluded."""

    def test_not_excluded(self) -> None:
        options = SimpleNamespace(exclude=["CVS", ".svn", ".git"])
        assert (
            optrecurse.RecursiveOptionParser.isexcluded(options, "somefile.po") is False
        )

    def test_excluded_exact(self) -> None:
        options = SimpleNamespace(exclude=["CVS", ".svn", ".git"])
        assert optrecurse.RecursiveOptionParser.isexcluded(options, "CVS") is True

    def test_excluded_in_path(self) -> None:
        options = SimpleNamespace(exclude=["CVS", ".svn", ".git"])
        assert (
            optrecurse.RecursiveOptionParser.isexcluded(
                options, os.path.join("path", "to", ".git")
            )
            is True
        )

    def test_excluded_fnmatch_pattern(self) -> None:
        options = SimpleNamespace(exclude=["*.bak"])
        assert optrecurse.RecursiveOptionParser.isexcluded(options, "file.bak") is True

    def test_not_excluded_partial_match(self) -> None:
        options = SimpleNamespace(exclude=["CVS"])
        assert (
            optrecurse.RecursiveOptionParser.isexcluded(options, "CVS_extra") is False
        )


class TestGetFormatHelp:
    """Tests for RecursiveOptionParser.getformathelp."""

    def test_empty_formats(self) -> None:
        assert optrecurse.RecursiveOptionParser.getformathelp([]) == ""

    def test_single_format(self) -> None:
        assert optrecurse.RecursiveOptionParser.getformathelp(["po"]) == "po format"

    def test_multiple_formats(self) -> None:
        result = optrecurse.RecursiveOptionParser.getformathelp(["po", "xliff"])
        assert result == "po, xliff formats"

    def test_none_filtered_out(self) -> None:
        result = optrecurse.RecursiveOptionParser.getformathelp([None, "po"])
        assert result == "po format"

    def test_only_none(self) -> None:
        assert optrecurse.RecursiveOptionParser.getformathelp([None]) == ""

    def test_formats_are_sorted(self) -> None:
        result = optrecurse.RecursiveOptionParser.getformathelp(["xliff", "po", "csv"])
        assert result == "csv, po, xliff formats"


class TestGetFullInputPath:
    """Tests for RecursiveOptionParser.getfullinputpath."""

    def test_with_input_dir(self) -> None:
        options = SimpleNamespace(input="/base/dir")
        result = optrecurse.RecursiveOptionParser.getfullinputpath(options, "file.txt")
        assert result == os.path.join("/base/dir", "file.txt")

    def test_without_input_dir(self) -> None:
        options = SimpleNamespace(input="")
        result = optrecurse.RecursiveOptionParser.getfullinputpath(options, "file.txt")
        assert result == "file.txt"

    def test_with_none_input(self) -> None:
        options = SimpleNamespace(input=None)
        result = optrecurse.RecursiveOptionParser.getfullinputpath(options, "file.txt")
        assert result == "file.txt"


class TestGetFullOutputPath:
    """Tests for RecursiveOptionParser.getfulloutputpath."""

    def test_recursive_with_output_dir(self) -> None:
        options = SimpleNamespace(recursiveoutput=True, output="/out/dir")
        result = optrecurse.RecursiveOptionParser.getfulloutputpath(options, "file.po")
        assert result == os.path.join("/out/dir", "file.po")

    def test_not_recursive(self) -> None:
        options = SimpleNamespace(recursiveoutput=False, output="/out/dir")
        result = optrecurse.RecursiveOptionParser.getfulloutputpath(options, "file.po")
        assert result == "file.po"

    def test_recursive_without_output_dir(self) -> None:
        options = SimpleNamespace(recursiveoutput=True, output=None)
        result = optrecurse.RecursiveOptionParser.getfulloutputpath(options, "file.po")
        assert result == "file.po"


class TestGetFullTemplatePath:
    """Tests for RecursiveOptionParser.getfulltemplatepath."""

    def test_recursive_template(self) -> None:
        parser = optrecurse.RecursiveOptionParser(
            {("txt", "pot"): ("po", None)}, usetemplates=True
        )
        options = SimpleNamespace(recursivetemplate=True, template="/templates/dir")
        result = parser.getfulltemplatepath(options, "file.pot")
        assert result == os.path.join("/templates/dir", "file.pot")

    def test_not_recursive_template(self) -> None:
        parser = optrecurse.RecursiveOptionParser(
            {("txt", "pot"): ("po", None)}, usetemplates=True
        )
        options = SimpleNamespace(
            recursivetemplate=False, template="/templates/file.pot"
        )
        result = parser.getfulltemplatepath(options, "file.pot")
        assert result == "file.pot"

    def test_no_template_path(self) -> None:
        parser = optrecurse.RecursiveOptionParser(
            {("txt", "pot"): ("po", None)}, usetemplates=True
        )
        options = SimpleNamespace(recursivetemplate=True, template="/templates/dir")
        result = parser.getfulltemplatepath(options, None)
        assert result is None

    def test_no_template_option(self) -> None:
        parser = optrecurse.RecursiveOptionParser(
            {("txt", "pot"): ("po", None)}, usetemplates=True
        )
        options = SimpleNamespace(recursivetemplate=True, template=None)
        result = parser.getfulltemplatepath(options, "file.pot")
        assert result is None


class TestSetFormats:
    """Tests for RecursiveOptionParser.setformats and format validation."""

    def test_simple_format_dict(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        assert "txt" in parser.inputformats
        assert (None, None) not in parser.outputoptions
        assert ("txt", None) in parser.outputoptions

    def test_format_with_templates(self) -> None:
        parser = optrecurse.RecursiveOptionParser(
            {("txt", "pot"): ("po", None)}, usetemplates=True
        )
        assert "txt" in parser.inputformats
        assert ("txt", "pot") in parser.outputoptions

    def test_format_list_of_tuples(self) -> None:
        formats = [("txt", ("po", None)), ("csv", ("po", None))]
        parser = optrecurse.RecursiveOptionParser(dict(formats))
        assert "txt" in parser.inputformats
        assert "csv" in parser.inputformats

    def test_invalid_formatgroup_type(self) -> None:
        with pytest.raises(TypeError, match="formatgroups must be tuples"):
            optrecurse.RecursiveOptionParser({123: ("po", None)})

    def test_invalid_formatgroup_length(self) -> None:
        with pytest.raises(ValueError, match="formatgroups must be tuples of length"):
            optrecurse.RecursiveOptionParser({("a", "b", "c"): ("po", None)})

    def test_invalid_output_options(self) -> None:
        with pytest.raises(ValueError, match="output options must be tuples"):
            optrecurse.RecursiveOptionParser({"txt": "po"})

    def test_none_input_format(self) -> None:
        parser = optrecurse.RecursiveOptionParser({None: ("po", None)})
        assert None in parser.inputformats


class TestGetOutputOptions:
    """Tests for RecursiveOptionParser.getoutputoptions."""

    def test_exact_match(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", _noop_processor)})
        fmt, proc = parser.getoutputoptions(None, "file.txt", None)
        assert fmt == "po"
        assert proc is _noop_processor

    def test_wildcard_input(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"*": ("po", _noop_processor)})
        fmt, _proc = parser.getoutputoptions(None, "file.txt", None)
        assert fmt == "po"

    def test_template_exact_match(self) -> None:
        parser = optrecurse.RecursiveOptionParser(
            {("txt", "pot"): ("po", _noop_processor)}, usetemplates=True
        )
        fmt, _proc = parser.getoutputoptions(None, "file.txt", "tmpl.pot")
        assert fmt == "po"

    def test_no_matching_format_raises(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        with pytest.raises(ValueError, match="don't know what to do"):
            parser.getoutputoptions(None, "file.csv", None)

    def test_no_input_ext_raises(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        with pytest.raises(ValueError, match="no file extension"):
            parser.getoutputoptions(None, None, None)

    def test_wildcard_output_uses_input_ext(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"*": ("*", _noop_processor)})
        fmt, _proc = parser.getoutputoptions(None, "file.txt", None)
        assert fmt == "txt"

    def test_no_match_with_templates_raises_with_both_formats(self) -> None:
        parser = optrecurse.RecursiveOptionParser(
            {("txt", "pot"): ("po", None)}, usetemplates=True
        )
        with pytest.raises(
            ValueError, match=r"input format .csv.*template format .xlf"
        ):
            parser.getoutputoptions(None, "file.csv", "tmpl.xlf")

    def test_no_match_with_templates_no_template(self) -> None:
        parser = optrecurse.RecursiveOptionParser(
            {("txt", "pot"): ("po", None)}, usetemplates=True
        )
        with pytest.raises(ValueError, match="no template file"):
            parser.getoutputoptions(None, "file.csv", None)

    def test_wildcard_template(self) -> None:
        parser = optrecurse.RecursiveOptionParser(
            {("txt", "*"): ("po", _noop_processor)}, usetemplates=True
        )
        fmt, _proc = parser.getoutputoptions(None, "file.txt", "tmpl.pot")
        assert fmt == "po"


class TestIsValidInputName:
    """Tests for RecursiveOptionParser.isvalidinputname."""

    def test_valid_extension(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        assert parser.isvalidinputname("file.txt") is True

    def test_invalid_extension(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        assert parser.isvalidinputname("file.csv") is False

    def test_wildcard_accepts_all(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"*": ("po", None)})
        assert parser.isvalidinputname("file.anything") is True

    def test_no_extension(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        assert parser.isvalidinputname("noextension") is False


class TestOpenInputFile:
    """Tests for RecursiveOptionParser.openinputfile."""

    def test_open_existing_file(self, tmp_path) -> None:
        f = tmp_path / "input.txt"
        f.write_bytes(b"test content")
        result = optrecurse.RecursiveOptionParser.openinputfile(None, str(f))
        try:
            assert result.read() == b"test content"
        finally:
            result.close()

    def test_open_stdin(self) -> None:
        # openinputfile returns sys.stdin when path is None; stdin must not be closed
        assert optrecurse.RecursiveOptionParser.openinputfile(None, None) is sys.stdin


class TestOpenTempOutputFile:
    """Tests for RecursiveOptionParser.opentempoutputfile."""

    def test_returns_bytesio(self) -> None:
        result = optrecurse.RecursiveOptionParser.opentempoutputfile(None, "output.po")
        assert isinstance(result, BytesIO)


class TestFinalizeTempOutputFile:
    """Tests for RecursiveOptionParser.finalizetempoutputfile."""

    def test_writes_to_final_file(self, tmp_path) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        outputpath = str(tmp_path / "output.po")
        tempfile = BytesIO(b"translated content")
        parser.finalizetempoutputfile(None, tempfile, outputpath)
        with open(outputpath, "rb") as f:
            assert f.read() == b"translated content"


class TestOpenTemplateFile:
    """Tests for RecursiveOptionParser.opentemplatefile."""

    def test_open_existing_template(self, tmp_path) -> None:
        f = tmp_path / "template.pot"
        f.write_bytes(b"template content")
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        result = parser.opentemplatefile(None, str(f))
        try:
            assert result.read() == b"template content"
        finally:
            result.close()

    def test_none_template_path(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        # No file is opened when template path is None
        result = parser.opentemplatefile(None, None)
        assert result is None

    def test_missing_template_returns_none(self, tmp_path) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        # No file is opened when template path doesn't exist
        result = parser.opentemplatefile(None, str(tmp_path / "missing.pot"))
        assert result is None


class TestMkdir:
    """Tests for RecursiveOptionParser.mkdir."""

    def test_create_single_subdir(self, tmp_path) -> None:
        optrecurse.RecursiveOptionParser.mkdir(str(tmp_path), "subdir")
        assert (tmp_path / "subdir").is_dir()

    def test_create_nested_subdir(self, tmp_path) -> None:
        optrecurse.RecursiveOptionParser.mkdir(
            str(tmp_path), os.path.join("a", "b", "c")
        )
        assert (tmp_path / "a" / "b" / "c").is_dir()

    def test_parent_must_exist(self) -> None:
        with pytest.raises(ValueError, match=r"parent.*does not exist"):
            optrecurse.RecursiveOptionParser.mkdir("/nonexistent/path", "subdir")


class TestCheckOutputSubdir:
    """Tests for RecursiveOptionParser.checkoutputsubdir."""

    def test_creates_subdir(self, tmp_path) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options = SimpleNamespace(output=str(tmp_path))
        parser.checkoutputsubdir(options, "sub")
        assert (tmp_path / "sub").is_dir()

    def test_existing_subdir_is_ok(self, tmp_path) -> None:
        (tmp_path / "sub").mkdir()
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options = SimpleNamespace(output=str(tmp_path))
        parser.checkoutputsubdir(options, "sub")
        assert (tmp_path / "sub").is_dir()


class TestGetOutputName:
    """Tests for RecursiveOptionParser.getoutputname."""

    def test_recursive_output(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options = SimpleNamespace(recursiveoutput=True, output="/out")
        result = parser.getoutputname(options, "file.txt", "po")
        assert result == "file" + os.extsep + "po"

    def test_non_recursive_returns_output_option(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options = SimpleNamespace(recursiveoutput=False, output="output.po")
        result = parser.getoutputname(options, "file.txt", "po")
        assert result == "output.po"

    def test_no_input_name_returns_output_option(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options = SimpleNamespace(recursiveoutput=True, output="output.po")
        result = parser.getoutputname(options, None, "po")
        assert result == "output.po"

    def test_no_output_format(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options = SimpleNamespace(recursiveoutput=True, output="/out")
        result = parser.getoutputname(options, "file.txt", None)
        assert result == "file"


class TestGetTemplateName:
    """Tests for RecursiveOptionParser.gettemplatename."""

    def test_no_templates(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options = SimpleNamespace(template=None, recursivetemplate=False)
        assert parser.gettemplatename(options, "file.txt") is None

    def test_non_recursive_returns_template_option(self) -> None:
        parser = optrecurse.RecursiveOptionParser(
            {("po", "pot"): ("po", None)}, usetemplates=True
        )
        options = SimpleNamespace(template="tmpl.pot", recursivetemplate=False)
        assert parser.gettemplatename(options, "file.po") == "tmpl.pot"

    def test_no_inputname_returns_template_option(self) -> None:
        parser = optrecurse.RecursiveOptionParser(
            {("po", "pot"): ("po", None)}, usetemplates=True
        )
        options = SimpleNamespace(template="tmpl.pot", recursivetemplate=False)
        assert parser.gettemplatename(options, None) == "tmpl.pot"

    def test_recursive_with_matching_template(self, tmp_path) -> None:
        parser = optrecurse.RecursiveOptionParser(
            {("po", "pot"): ("po", None)}, usetemplates=True
        )
        (tmp_path / "file.pot").write_text("template")
        options = SimpleNamespace(template=str(tmp_path), recursivetemplate=True)
        assert parser.gettemplatename(options, "file.po") == "file.pot"

    def test_recursive_no_matching_template(self, tmp_path) -> None:
        parser = optrecurse.RecursiveOptionParser(
            {("po", "pot"): ("po", None)}, usetemplates=True
        )
        options = SimpleNamespace(template=str(tmp_path), recursivetemplate=True)
        assert parser.gettemplatename(options, "file.po") is None


class TestGetUsageString:
    """Tests for RecursiveOptionParser.getusagestring."""

    def test_required_option(self) -> None:
        option = optparse.Option("-i", "--input", dest="input", metavar="INPUT")
        option.required = True  # type: ignore[attr-defined]
        result = optrecurse.RecursiveOptionParser.getusagestring(option)
        assert result == "-i|--input INPUT"

    def test_optional_option(self) -> None:
        option = optparse.Option("-o", "--output", dest="output", metavar="OUTPUT")
        result = optrecurse.RecursiveOptionParser.getusagestring(option)
        assert result == "[-o|--output OUTPUT]"

    def test_optional_switch(self) -> None:
        option = optparse.Option("-v", "--verbose", dest="verbose")
        option.optionalswitch = True  # type: ignore[attr-defined]
        result = optrecurse.RecursiveOptionParser.getusagestring(option)
        assert "[-v|--verbose]" in result

    def test_no_metavar(self) -> None:
        option = optparse.Option("--flag", dest="flag")
        result = optrecurse.RecursiveOptionParser.getusagestring(option)
        assert result == "[--flag]"


class TestGetUsageMan:
    """Tests for RecursiveOptionParser.getusageman."""

    def test_required_option(self) -> None:
        option = optparse.Option("-i", "--input", dest="input", metavar="INPUT")
        option.required = True  # type: ignore[attr-defined]
        result = optrecurse.RecursiveOptionParser.getusageman(option)
        assert "-i" in result
        assert "--input" in result
        assert "INPUT" in result

    def test_optional_option_wrapped(self) -> None:
        option = optparse.Option("--flag", dest="flag")
        result = optrecurse.RecursiveOptionParser.getusageman(option)
        assert "\\fR[\\fP" in result
        assert "\\fR]\\fP" in result


class TestDefineOption:
    """Tests for RecursiveOptionParser.define_option."""

    def test_adds_new_option(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        new_opt = optparse.Option("--newopt", dest="newopt", default="val")
        parser.define_option(new_opt)
        assert parser.has_option("--newopt")

    def test_replaces_existing_short_option(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        assert parser.has_option("-i")
        new_opt = optparse.Option("-i", "--newinput", dest="newinput")
        parser.define_option(new_opt)
        assert parser.has_option("--newinput")

    def test_replaces_existing_long_option(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        assert parser.has_option("--input")
        new_opt = optparse.Option("--input", dest="newinput")
        parser.define_option(new_opt)
        assert parser.has_option("--input")


class TestGetPassthroughOptions:
    """Tests for RecursiveOptionParser.getpassthroughoptions."""

    def test_empty_passthrough(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options = SimpleNamespace(input="file.txt", output="file.po")
        result = parser.getpassthroughoptions(options)
        assert result == {}

    def test_passthrough_extracts_values(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        parser.passthrough.append("personality")
        options = SimpleNamespace(personality="java", input="f.txt")
        result = parser.getpassthroughoptions(options)
        assert result == {"personality": "java"}

    def test_passthrough_missing_attribute(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        parser.passthrough.append("nonexistent")
        options = SimpleNamespace(input="f.txt")
        result = parser.getpassthroughoptions(options)
        assert "nonexistent" not in result


class TestWarning:
    """Tests for RecursiveOptionParser.warning."""

    def test_warning_no_options(self, caplog) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        with caplog.at_level(logging.WARNING):
            parser.warning("test warning")
        assert "test warning" in caplog.text

    def test_warning_message_errorlevel(self, caplog) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options = SimpleNamespace(errorlevel="message")
        exc_info = _make_exc_info(ValueError("test error"))
        with caplog.at_level(logging.WARNING):
            parser.warning("processing failed", options, exc_info)
        assert "test error" in caplog.text

    def test_warning_none_errorlevel(self, caplog) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options = SimpleNamespace(errorlevel="none")
        with caplog.at_level(logging.WARNING):
            parser.warning("test warning", options)
        assert "test warning" in caplog.text

    def test_warning_exception_errorlevel(self, caplog) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options = SimpleNamespace(errorlevel="exception")
        exc_info = _make_exc_info(ValueError("exc detail"))
        with caplog.at_level(logging.WARNING):
            parser.warning("err", options, exc_info)
        assert "exc detail" in caplog.text

    def test_warning_traceback_errorlevel(self, caplog) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options = SimpleNamespace(errorlevel="traceback")
        exc_info = _make_exc_info(ValueError("tb detail"))
        with caplog.at_level(logging.WARNING):
            parser.warning("err", options, exc_info)
        assert "Traceback" in caplog.text
        assert "tb detail" in caplog.text


class TestParseArgs:
    """Tests for RecursiveOptionParser.parse_args."""

    def test_explicit_input_and_output(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options, _args = parser.parse_args(["-i", "input.txt", "-o", "output.po"])
        assert options.input == "input.txt"
        assert options.output == "output.po"

    def test_implicit_input_from_args(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options, _args = parser.parse_args(["input.txt"])
        assert options.input == "input.txt"

    def test_implicit_input_and_output(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options, _args = parser.parse_args(["input.txt", "output.po"])
        assert options.input == "input.txt"
        assert options.output == "output.po"

    def test_stdin_dash(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options, _args = parser.parse_args(["-i", "-", "-o", "output.po"])
        assert options.input is None
        assert options.output == "output.po"

    def test_no_input_raises(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_single_item_list_is_unwrapped(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options, _args = parser.parse_args(["-i", "only.txt"])
        assert options.input == "only.txt"
        assert not isinstance(options.input, list)

    def test_multiple_inputs(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options, _args = parser.parse_args(
            ["-i", "a.txt", "-i", "b.txt", "-o", "output.po"]
        )
        assert isinstance(options.input, list)
        assert "a.txt" in options.input
        assert "b.txt" in options.input


class TestProcessFile:
    """Tests for RecursiveOptionParser.processfile."""

    def test_successful_processing(self, tmp_path) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        infile = tmp_path / "input.txt"
        outfile = tmp_path / "output.po"
        infile.write_bytes(b"hello")

        def processor(inputfile, outputfile, templatefile):
            outputfile.write(inputfile.read())
            return True

        result = parser.processfile(
            processor, SimpleNamespace(), str(infile), str(outfile), None
        )
        assert result is True
        assert outfile.read_bytes() == b"hello"

    def test_failed_processing_removes_output(self, tmp_path) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        infile = tmp_path / "input.txt"
        outfile = tmp_path / "output.po"
        infile.write_bytes(b"hello")

        def processor(inputfile, outputfile, templatefile):
            outputfile.write(b"partial")
            return False

        result = parser.processfile(
            processor, SimpleNamespace(), str(infile), str(outfile), None
        )
        assert result is False
        assert not outfile.exists()

    def test_temp_output_when_input_equals_output(self, tmp_path) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        filepath = tmp_path / "inplace.txt"
        filepath.write_bytes(b"original")

        def processor(inputfile, outputfile, templatefile):
            data = inputfile.read()
            outputfile.write(data + b" modified")
            return True

        result = parser.processfile(
            processor, SimpleNamespace(), str(filepath), str(filepath), None
        )
        assert result is True
        assert filepath.read_bytes() == b"original modified"


class TestRecurseInputFileList:
    """
    Tests for RecursiveOptionParser.recurseinputfilelist.

    This covers the fix from PR #6158 (commonpath vs commonprefix).
    """

    @staticmethod
    def _verify_roundtrip(original_inputs, result, options_input):
        """Verify that relative paths joined with base dir reconstruct originals."""
        reconstructed = sorted(os.path.join(options_input, r) for r in result)
        assert reconstructed == sorted(original_inputs)

    def test_common_base_directory(self, tmp_path) -> None:
        """Test that files sharing a common directory are resolved correctly."""
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        subdir = tmp_path / "project"
        subdir.mkdir()
        (subdir / "a.txt").write_text("a")
        (subdir / "b.txt").write_text("b")

        original = [str(subdir / "a.txt"), str(subdir / "b.txt")]
        options = SimpleNamespace(input=list(original), exclude=[])
        result = parser.recurseinputfilelist(options)
        assert len(result) == 2
        self._verify_roundtrip(original, result, options.input)

    def test_commonpath_not_commonprefix(self, tmp_path) -> None:
        """
        Test the fix from PR #6158.

        os.path.commonprefix operates on characters and can split in the
        middle of a path component (e.g., /home/abc and /home/abx would
        give /home/ab). os.path.commonpath correctly operates on path
        components and always returns a valid directory boundary.
        """
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        # Create directories with a common character prefix but different names
        dir_abc = tmp_path / "abc"
        dir_abx = tmp_path / "abx"
        dir_abc.mkdir()
        dir_abx.mkdir()
        (dir_abc / "file1.txt").write_text("1")
        (dir_abx / "file2.txt").write_text("2")

        original = [str(dir_abc / "file1.txt"), str(dir_abx / "file2.txt")]
        options = SimpleNamespace(input=list(original), exclude=[])
        result = parser.recurseinputfilelist(options)

        # The base dir must be a real directory (not split mid-component)
        assert os.path.isdir(options.input)
        self._verify_roundtrip(original, result, options.input)

        # With the old commonprefix, the prefix "/path/ab" would be split
        # mid-component, but dirname would fix it. With commonpath, the
        # common path is correctly "/path" (tmp_path), so dirname goes up
        # one more level. Either way, relative paths must round-trip.
        for relpath in result:
            assert os.path.isfile(os.path.join(options.input, relpath))

    def test_excluded_files_are_filtered(self, tmp_path) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        subdir = tmp_path / "project"
        subdir.mkdir()
        (subdir / "a.txt").write_text("a")
        (subdir / "b.bak").write_text("b")

        options = SimpleNamespace(
            input=[str(subdir / "a.txt"), str(subdir / "b.bak")],
            exclude=["*.bak"],
        )
        result = parser.recurseinputfilelist(options)
        # Only a.txt should remain; b.bak excluded
        assert len(result) == 1
        assert any("a.txt" in r for r in result)
        assert not any("b.bak" in r for r in result)

    def test_single_file_in_list(self, tmp_path) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        subdir = tmp_path / "project"
        subdir.mkdir()
        filepath = subdir / "only.txt"
        filepath.write_text("content")

        original = [str(filepath)]
        options = SimpleNamespace(input=list(original), exclude=[])
        result = parser.recurseinputfilelist(options)
        assert len(result) == 1
        assert os.path.isfile(os.path.join(options.input, result[0]))

    def test_files_in_nested_dirs(self, tmp_path) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        dir_a = tmp_path / "sub" / "a"
        dir_b = tmp_path / "sub" / "b"
        dir_a.mkdir(parents=True)
        dir_b.mkdir(parents=True)
        (dir_a / "f1.txt").write_text("1")
        (dir_b / "f2.txt").write_text("2")

        original = [str(dir_a / "f1.txt"), str(dir_b / "f2.txt")]
        options = SimpleNamespace(input=list(original), exclude=[])
        result = parser.recurseinputfilelist(options)
        assert len(result) == 2
        self._verify_roundtrip(original, result, options.input)
        for relpath in result:
            assert os.path.isfile(os.path.join(options.input, relpath))


class TestRecurseInputFiles:
    """Tests for RecursiveOptionParser.recurseinputfiles."""

    def test_finds_matching_files(self, tmp_path) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.txt").write_text("content2")
        (tmp_path / "file3.csv").write_text("content3")

        options = SimpleNamespace(input=str(tmp_path), exclude=["CVS", ".svn", ".git"])
        result = parser.recurseinputfiles(options)
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "file3.csv" not in result

    def test_recurses_subdirectories(self, tmp_path) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        subdir = tmp_path / "sub"
        subdir.mkdir()
        (tmp_path / "file1.txt").write_text("content1")
        (subdir / "file2.txt").write_text("content2")

        options = SimpleNamespace(input=str(tmp_path), exclude=["CVS", ".svn", ".git"])
        result = parser.recurseinputfiles(options)
        assert "file1.txt" in result
        assert os.path.join("sub", "file2.txt") in result

    def test_excludes_directories(self, tmp_path) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "file.txt").write_text("excluded")
        (tmp_path / "file.txt").write_text("included")

        options = SimpleNamespace(input=str(tmp_path), exclude=["CVS", ".svn", ".git"])
        result = parser.recurseinputfiles(options)
        assert "file.txt" in result
        assert os.path.join(".git", "file.txt") not in result

    def test_wildcard_format_accepts_all(self, tmp_path) -> None:
        parser = optrecurse.RecursiveOptionParser({"*": ("po", None)})
        (tmp_path / "file.txt").write_text("text")
        (tmp_path / "file.csv").write_text("csv")

        options = SimpleNamespace(input=str(tmp_path), exclude=[])
        result = parser.recurseinputfiles(options)
        assert "file.txt" in result
        assert "file.csv" in result


class TestSplitInputExt:
    """Tests for splitinputext and splittemplateext."""

    def test_splitinputext(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        assert parser.splitinputext("file.txt") == ("file", "txt")

    def test_splittemplateext(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        assert parser.splittemplateext("file.pot") == ("file", "pot")

    def test_splitext_no_extension(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        assert parser.splitext("noext") == ("noext", "")

    def test_splitext_with_path(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        root, ext = parser.splitext(os.path.join("dir", "file.txt"))
        assert root == os.path.join("dir", "file")
        assert ext == "txt"


class TestStdoutWrapper:
    """Tests for the StdoutWrapper class."""

    def test_write_text(self, capsys) -> None:
        wrapper = optrecurse.StdoutWrapper()
        wrapper.write("hello text")
        captured = capsys.readouterr()
        assert captured.out == "hello text"

    def test_write_bytes_utf8(self, capsys) -> None:
        wrapper = optrecurse.StdoutWrapper()
        wrapper.write(b"hello bytes")
        captured = capsys.readouterr()
        assert captured.out == "hello bytes"

    def test_write_bytes_non_utf8(self, capsys) -> None:
        wrapper = optrecurse.StdoutWrapper()
        wrapper.write(b"\xff\xfe")
        captured = capsys.readouterr()
        assert "Unable to write binary content" in captured.out

    def test_delegates_attributes(self) -> None:
        wrapper = optrecurse.StdoutWrapper()
        assert hasattr(wrapper, "fileno")


class TestManHelpFormatter:
    """Tests for the ManHelpFormatter class."""

    def test_format_option_strings_with_metavar(self) -> None:
        formatter = optrecurse.ManHelpFormatter()
        option = optparse.Option("-i", "--input", dest="input", metavar="INPUT")
        result = formatter.format_option_strings(option)
        assert "\\fI" in result
        assert "INPUT" in result

    def test_format_option_strings_no_metavar(self) -> None:
        formatter = optrecurse.ManHelpFormatter()
        option = optparse.Option("--flag", dest="flag", action="store_true")
        result = formatter.format_option_strings(option)
        assert "--flag" in result


class TestProgressBar:
    """Tests for the ProgressBar class."""

    def test_dots_progress(self) -> None:
        pb = optrecurse.ProgressBar("dots", ["a", "b"])
        pb.report_progress("a", True)

    def test_none_progress(self) -> None:
        pb = optrecurse.ProgressBar("none", ["a"])
        pb.report_progress("a", True)

    def test_bar_progress(self) -> None:
        pb = optrecurse.ProgressBar("bar", ["a", "b", "c"])
        pb.report_progress("a", True)

    def test_names_progress(self) -> None:
        pb = optrecurse.ProgressBar("names", ["a"])
        pb.report_progress("a", True)

    def test_verbose_progress(self) -> None:
        pb = optrecurse.ProgressBar("verbose", ["a", "b"])
        pb.report_progress("a", True)


class TestFormatManpage:
    """Tests for format_manpage and print_manpage."""

    def test_format_manpage(self) -> None:
        parser = optrecurse.RecursiveOptionParser(
            {"txt": ("po", None)}, description="A test converter.\n\nMore details."
        )
        manpage = parser.format_manpage()
        assert ".TH" in manpage
        assert ".SH NAME" in manpage
        assert ".SH SYNOPSIS" in manpage
        assert ".SH OPTIONS" in manpage

    def test_print_manpage(self) -> None:
        parser = optrecurse.RecursiveOptionParser(
            {"txt": ("po", None)}, description="A test converter.\n\nMore details."
        )
        buf = StringIO()
        parser.print_manpage(file=buf)
        assert ".TH" in buf.getvalue()


class TestSetUsage:
    """Tests for set_usage."""

    def test_auto_usage(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        parser.set_usage()
        assert parser.usage is not None
        assert "%prog" in parser.usage

    def test_custom_usage(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        parser.set_usage("custom usage")
        assert "custom" in parser.get_usage()


class TestEnsureRecursiveOutputDirExists:
    """Tests for ensurerecursiveoutputdirexists."""

    def test_creates_output_dir(self, tmp_path) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        outdir = tmp_path / "newoutput"
        options = SimpleNamespace(output=str(outdir))
        parser.ensurerecursiveoutputdirexists(options)
        assert outdir.is_dir()

    def test_existing_output_dir_ok(self, tmp_path) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options = SimpleNamespace(output=str(tmp_path))
        # Should not raise; tmp_path is already a directory
        parser.ensurerecursiveoutputdirexists(options)

    def test_no_output_raises(self) -> None:
        parser = optrecurse.RecursiveOptionParser({"txt": ("po", None)})
        options = SimpleNamespace(output=None)
        with pytest.raises(SystemExit):
            parser.ensurerecursiveoutputdirexists(options)


class TestRecursiveProcess:
    """Tests for recursiveprocess with file system setup."""

    def test_processes_single_file(self, tmp_path) -> None:
        processed = []

        def processor(inputfile, outputfile, templatefile):
            processed.append(True)
            outputfile.write(inputfile.read())
            return True

        parser = optrecurse.RecursiveOptionParser({"txt": ("po", processor)})
        infile = tmp_path / "input.txt"
        outfile = tmp_path / "output.po"
        infile.write_bytes(b"content")

        options = SimpleNamespace(
            input=str(infile),
            output=str(outfile),
            template=None,
            progress="none",
            errorlevel="message",
            exclude=["CVS", ".svn", ".git"],
        )
        parser.recursiveprocess(options)
        assert len(processed) == 1
        assert outfile.read_bytes() == b"content"

    def test_processes_directory_recursively(self, tmp_path) -> None:
        processed_files = []

        def processor(inputfile, outputfile, templatefile):
            processed_files.append(True)
            outputfile.write(inputfile.read())
            return True

        parser = optrecurse.RecursiveOptionParser({"txt": ("po", processor)})
        indir = tmp_path / "in"
        outdir = tmp_path / "out"
        indir.mkdir()
        outdir.mkdir()
        (indir / "a.txt").write_bytes(b"a")
        (indir / "b.txt").write_bytes(b"b")

        options = SimpleNamespace(
            input=str(indir),
            output=str(outdir),
            template=None,
            progress="none",
            errorlevel="message",
            exclude=["CVS", ".svn", ".git"],
        )
        parser.recursiveprocess(options)
        assert len(processed_files) == 2

    def test_handles_processing_errors(self, tmp_path, caplog) -> None:
        def processor(inputfile, outputfile, templatefile):
            raise RuntimeError("processing failed")

        parser = optrecurse.RecursiveOptionParser({"txt": ("po", processor)})
        infile = tmp_path / "input.txt"
        outfile = tmp_path / "output.po"
        infile.write_bytes(b"content")

        options = SimpleNamespace(
            input=str(infile),
            output=str(outfile),
            template=None,
            progress="none",
            errorlevel="message",
            exclude=["CVS", ".svn", ".git"],
        )
        with caplog.at_level(logging.WARNING):
            parser.recursiveprocess(options)
        assert "Error processing" in caplog.text

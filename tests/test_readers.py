from __future__ import absolute_import

from central.exceptions import LibraryRequiredError
from central.readers import add_reader, get_reader, remove_reader, IniReader, JsonReader, TomlReader, YamlReader
from central.structures import IgnoreCaseDict
from io import StringIO
from unittest import TestCase


class ReaderMixin(object):
    def test_read_with_none_as_stream(self):
        with self.assertRaises(ValueError):
            self.reader.read(None)

    def test_read_valid_stream(self):
        stream = StringIO()
        stream.write(self.data)
        stream.seek(0, 0)

        data = self.reader.read(stream)
        self.assertEqual(data, {'database': {'host': 'localhost', 'port': '1234'}})

    def test_read_ignore_case(self):
        stream = StringIO()
        stream.write(self.data)
        stream.seek(0, 0)

        data = self.reader.read(stream)

        self.assertIsInstance(data, IgnoreCaseDict)

        self.assertEqual(data.get('Database'), {'host': 'localhost', 'port': '1234'})
        self.assertEqual(data.get('Database').get('Host'), 'localhost')


class TestIniReader(TestCase, ReaderMixin):
    def setUp(self):
        self.reader = IniReader()
        self.data = u'[database]\nhost=localhost\nport=1234\n'


class TestJsonReader(TestCase, ReaderMixin):
    def setUp(self):
        self.reader = JsonReader()
        self.data = u'{"database": {"host": "localhost", "port": "1234"}}'


class TestTomlReader(TestCase, ReaderMixin):
    def setUp(self):
        self.reader = TomlReader()
        self.data = u'[database]\nhost="localhost"\nport="1234"\n'

    def test_library_not_installed(self):
        from central import readers
        toml_tmp = readers.toml
        readers.toml = None

        with self.assertRaises(LibraryRequiredError):
            TomlReader()

        readers.toml = toml_tmp


class TestYamlReader(TestCase, ReaderMixin):
    def setUp(self):
        self.reader = YamlReader()
        self.data = u'database:\n  host: localhost\n  port: "1234"\n'

    def test_library_not_installed(self):
        from central import readers
        yaml_tmp = readers.yaml
        readers.yaml = None

        with self.assertRaises(LibraryRequiredError):
            YamlReader()

        readers.yaml = yaml_tmp


class TestManageRenders(TestCase):
    def test_add_render_with_valid_parameters(self):
        add_reader('render', JsonReader)
        self.assertEqual(get_reader('render'), JsonReader)

    def test_add_render_with_none_as_name(self):
        with self.assertRaises(TypeError):
            add_reader(None, JsonReader)

    def test_add_render_with_integer_as_name(self):
        with self.assertRaises(TypeError):
            add_reader(123, JsonReader)

    def test_add_render_with_none_as_render_cls(self):
        with self.assertRaises(ValueError):
            add_reader('render', None)

    def test_get_render_with_valid_name(self):
        add_reader('render', JsonReader)
        self.assertEqual(get_reader('render'), JsonReader)

    def test_get_render_with_invalid_name(self):
        self.assertIsNone(get_reader('not_found'))

    def test_get_render_with_none_as_name(self):
        with self.assertRaises(TypeError):
            get_reader(None)

    def test_get_render_with_integer_as_name(self):
        with self.assertRaises(TypeError):
            get_reader(123)

    def test_remove_render_with_none_as_name(self):
        with self.assertRaises(TypeError):
            remove_reader(None)

    def test_remove_render_with_integer_as_name(self):
        with self.assertRaises(TypeError):
            remove_reader(123)

    def test_remove_render_with_valid_name(self):
        add_reader('render', JsonReader)
        self.assertEqual(remove_reader('render'), JsonReader)

    def test_remove_render_with_invalid_name(self):
        self.assertIsNone(remove_reader('not_found'))

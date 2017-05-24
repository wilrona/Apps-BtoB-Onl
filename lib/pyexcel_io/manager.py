"""
    pyexcel_io.manager
    ~~~~~~~~~~~~~~~~~~~

    factory for getting readers and writers

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
import pkgutil
import logging
from itertools import chain

from pyexcel_io._compact import StringIO, BytesIO
import pyexcel_io.utils as ioutils
from collections import defaultdict


log = logging.getLogger(__name__)

soft_register = defaultdict(list)
reader_factories = {}
writer_factories = {}
text_stream_types = []
binary_stream_types = []
file_types = ()
mime_types = {}


ERROR_MESSAGE_FORMATTER = "one of these plugins for %s data in '%s': %s"
UPGRADE_MESSAGE = "Please upgrade the plugin '%s' according to \
plugin compactibility table."


def load_plugins(prefix, path, black_list):
    module_names = (module_info[1] for module_info in pkgutil.iter_modules()
                    if module_info[2] and module_info[1].startswith(prefix))

    module_names_from_pyinstaller = load_from_pyinstaller(prefix, path)
    # loop through modules and find our plug ins
    for module_name in chain(module_names, module_names_from_pyinstaller):

        if module_name in black_list:
            continue

        try:
            plugin = __import__(module_name)
            if hasattr(plugin, '__pyexcel_io_plugins__'):
                for plugin_meta in plugin.__pyexcel_io_plugins__:
                    pre_register(plugin_meta, module_name)
        except ImportError:
            continue


# load modules to work based with and without pyinstaller
# from: https://github.com/webcomics/dosage/blob/master/dosagelib/loader.py
# see: https://github.com/pyinstaller/pyinstaller/issues/1905
# load modules using iter_modules()
# (should find all plug ins in normal build, but not pyinstaller)
def load_from_pyinstaller(prefix, path):
    # special handling for PyInstaller
    table_of_content = set()
    for a_toc in (importer.toc for importer in map(pkgutil.get_importer, path)
                  if hasattr(importer, 'toc')):
        table_of_content |= a_toc

    for module_name in table_of_content:
        if module_name.startswith(prefix) and '.' not in module_name:
            yield module_name


class NoSupportingPluginFound(Exception):
    pass


class SupportingPluginAvailableButNotInstalled(Exception):
    pass


class UpgradePlugin(Exception):
    pass


def pre_register(plugin_meta, module_name):
    if not isinstance(plugin_meta, dict):
        plugin = module_name.replace('_', '-')
        raise UpgradePlugin(UPGRADE_MESSAGE % plugin)
    library_import_path = "%s.%s" % (module_name, plugin_meta['submodule'])
    for file_type in plugin_meta['file_types']:
        soft_register[file_type].append(
            (library_import_path, plugin_meta['submodule']))
        register_stream_type(file_type, plugin_meta['stream_type'])
    log.debug("pre-register :" + ','.join(plugin_meta['file_types']))


def dynamic_load_library(library_import_path):
    plugin = __import__(library_import_path[0])
    submodule = getattr(plugin, library_import_path[1])
    register_readers_and_writers(submodule.exports)


def get_writers():
    return writer_factories.keys()


def register_readers_and_writers(plugins):
    __debug_writer_file_types = []
    __debug_reader_file_types = []
    for plugin in plugins:
        the_file_type = plugin['file_type']
        register_a_file_type(
            the_file_type, plugin.get('stream_type', None),
            plugin.get('mime_type', None))
        if 'reader' in plugin:
            _register_a_reader(
                the_file_type, plugin['reader'], plugin['library'])
            __debug_reader_file_types.append(plugin['file_type'])
        if 'writer' in plugin:
            _register_a_writer(
                the_file_type, plugin['writer'], plugin['library'])
            __debug_writer_file_types.append(plugin['file_type'])
        # else:
            # ignored for now
    log.debug("register writers for:" + ",".join(__debug_writer_file_types))
    log.debug("register readers for:" + ",".join(__debug_reader_file_types))


def register_a_file_type(file_type, stream_type, mime_type):
    global file_types
    file_types += (file_type,)
    stream_type = stream_type
    if mime_type is not None:
        mime_types[file_type] = mime_type
    register_stream_type(file_type, stream_type)


def register_stream_type(file_type, stream_type):
    if stream_type == 'text':
        text_stream_types.append(file_type)
    elif stream_type == 'binary':
        binary_stream_types.append(file_type)


def get_io(file_type):
    """A utility function to help you generate a correct io stream

    :param file_type: a supported file type
    :returns: a appropriate io stream, None otherwise
    """
    __file_type = None
    if file_type:
        __file_type = file_type.lower()

    if __file_type in text_stream_types:
        return StringIO()
    elif __file_type in binary_stream_types:
        return BytesIO()
    else:
        return None


def get_io_type(file_type):
    """A utility function to help you generate a correct io stream

    :param file_type: a supported file type
    :returns: a appropriate io stream, None otherwise
    """
    __file_type = None
    if file_type:
        __file_type = file_type.lower()

    if __file_type in text_stream_types:
        return "string"
    elif __file_type in binary_stream_types:
        return "bytes"
    else:
        return None


def _register_a_reader(file_type, reader_class, library):
    _add_a_handler(reader_factories,
                   file_type, reader_class, library)


def _register_a_writer(file_type, writer_class, library):
    _add_a_handler(writer_factories,
                   file_type, writer_class, library)


def _add_a_handler(factories, file_type, handler, library):
    if file_type not in factories:
        factories[file_type] = {}
    factories[file_type][library] = handler


def create_reader(file_type, library=None):
    _preload_a_handler(reader_factories, file_type)
    try:
        reader = _get_a_handler(
            reader_factories, file_type, library)
        return reader
    except NoSupportingPluginFound:
        plugins = ioutils.AVAILABLE_READERS.get(file_type, None)
        if plugins:
            message = "Please install "
            if len(plugins) > 1:
                message += ERROR_MESSAGE_FORMATTER % (
                    'read', file_type, ','.join(plugins))
            else:
                message += plugins[0]
            raise SupportingPluginAvailableButNotInstalled(message)
        else:
            raise


def create_writer(file_type, library=None):
    _preload_a_handler(writer_factories, file_type)
    try:
        writer = _get_a_handler(
            writer_factories, file_type, library)
        return writer
    except NoSupportingPluginFound:
        plugins = ioutils.AVAILABLE_WRITERS.get(file_type, None)
        if plugins:
            message = "Please install "
            if len(plugins) > 1:
                message += ERROR_MESSAGE_FORMATTER % (
                    'write', file_type, ','.join(plugins))
            else:
                message += plugins[0]
            raise SupportingPluginAvailableButNotInstalled(message)
        else:
            raise


def _preload_a_handler(factories, file_type):
    __file_type = file_type.lower()
    if __file_type in soft_register:
        debug_path = []
        for path in soft_register[__file_type]:
            dynamic_load_library(path)
            debug_path.append(path)
        log.debug("preload :" + __file_type + ":" + ','.join(path))
        # once loaded, forgot it
        soft_register.pop(__file_type)


def _get_a_handler(factories, file_type, library):
    __file_type = file_type.lower()
    if __file_type in factories:
        handler_dict = factories[__file_type]
        if library is not None:
            handler_class = handler_dict.get(library, None)
            if handler_class is None:
                raise Exception("%s is not installed" % library)
        else:
            for _, _handler in handler_dict.items():
                handler_class = _handler
                break
        handler = handler_class()
        handler.set_type(__file_type)
        return handler
    raise NoSupportingPluginFound(
        "No suitable library found for %s" % file_type)

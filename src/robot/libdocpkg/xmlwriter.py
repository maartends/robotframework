#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os.path

from robot.utils import XmlWriter, get_timestamp

from .htmlwriter import DocToHtml


class LibdocXmlWriter(object):

    def __init__(self, force_html_doc=False):
        self._force_html_doc = force_html_doc

    def write(self, libdoc, outfile):
        formatter = DocFormatter(libdoc.doc_format, self._force_html_doc)
        writer = XmlWriter(outfile, usage='Libdoc output')
        self._write_start(libdoc, writer, formatter)
        self._write_keywords('init', libdoc.inits, libdoc.source,
                             writer, formatter)
        self._write_keywords('kw', libdoc.keywords, libdoc.source,
                             writer, formatter)
        self._write_end(writer)

    def _write_start(self, libdoc, writer, formatter):
        attrs = {'name': libdoc.name,
                 'type': libdoc.type,
                 'format': formatter.format,
                 'generated': get_timestamp(millissep=None)}
        self._add_source_info(attrs, libdoc, writer.output)
        writer.start('keywordspec', attrs)
        writer.element('version', libdoc.version)
        writer.element('scope', libdoc.scope)
        writer.element('namedargs', 'yes' if libdoc.named_args else 'no')
        writer.element('doc', formatter(libdoc.doc))

    def _add_source_info(self, attrs, item, outfile, lib_source=None):
        if item.source and item.source != lib_source:
            attrs['source'] = self._format_source(item.source, outfile)
        if item.lineno > 0:
            attrs['lineno'] = str(item.lineno)

    def _format_source(self, source, outfile):
        if not (os.path.exists(source)
                and hasattr(outfile, 'name')
                and os.path.isfile(outfile.name)):
            return source
        return os.path.relpath(source, os.path.dirname(outfile.name))

    def _write_keywords(self, kw_type, keywords, lib_source, writer, formatter):
        for kw in keywords:
            attrs = self._get_start_attrs(kw_type, kw, lib_source, writer)
            writer.start(kw_type, attrs)
            writer.start('arguments')
            for arg in kw.args:
                writer.element('arg', arg)
            writer.end('arguments')
            writer.element('doc', formatter(kw.doc))
            writer.start('tags')
            for tag in kw.tags:
                writer.element('tag', tag)
            writer.end('tags')
            writer.end(kw_type)

    def _get_start_attrs(self, kw_type, kw, lib_source, writer):
        if kw_type == 'init':
            attrs = {}
        else:
            attrs = {'name': kw.name,
                     'deprecated': 'true' if kw.deprecated else 'false'}
        self._add_source_info(attrs, kw, writer.output, lib_source)
        return attrs

    def _write_end(self, writer):
        writer.end('keywordspec')
        writer.close()


class DocFormatter(object):

    def __init__(self, doc_format, force_html=False):
        if force_html:
            self._formatter = DocToHtml(doc_format)
            self.format = 'HTML'
        else:
            self._formatter = lambda doc: doc
            self.format = doc_format

    def __call__(self, doc):
        return self._formatter(doc)

#!/usr/bin/env python3
import logging

import attr
from flake8 import checker
from flake8.plugins.pyflakes import FlakesChecker

__version__ = '16.12.0'

LOG = logging.getLogger('flake8.pyi')


class PyiAwareFlakesChecker(FlakesChecker):
    def deferHandleNode(self, node, parent):
        self.deferFunction(lambda: self.handleNode(node, parent))

    def LAMBDA(self, node):
        """This is likely very brittle, currently works for pyflakes 1.3.0.

        Deferring annotation handling depends on the fact that during calls
        to LAMBDA visiting the function's body is already deferred and the
        only eager calls to `handleNode` are for annotations.
        """
        self.handleNode, self.deferHandleNode = self.deferHandleNode, self.handleNode
        super().LAMBDA(node)
        self.handleNode, self.deferHandleNode = self.deferHandleNode, self.handleNode


class PyiAwareFileChecker(checker.FileChecker):
    def run_check(self, plugin, **kwargs):
        if self.filename.endswith('.pyi') and plugin['plugin'] == FlakesChecker:
            LOG.info(
                'Replacing FlakesChecker with PyiAwareFlakesChecker while '
                'checking %r',
                self.filename,
            )
            plugin = dict(plugin)
            plugin['plugin'] = PyiAwareFlakesChecker
        return super().run_check(plugin, **kwargs)


@attr.s
class PyiTreeChecker:
    name = 'flake8-pyi'
    version = __version__

    tree = attr.ib(default=None)
    filename = attr.ib(default='(none)')

    def run(self):
        return ()

    @classmethod
    def add_options(cls, parser):
        """This is brittle, there's multiple levels of caching of defaults."""
        for option in parser.options:
            if option.long_option_name == '--filename':
                option.default = '*.py,*.pyi'
                option.option_kwargs['default'] = option.default
                option.to_optparse().default = option.default
                parser.parser.defaults[option.dest] = option.default

        parser.add_option(
            '--no-pyi-aware-file-checker', default=False, action='store_true',
            parse_from_config=True,
            help="don't patch flake8 with .pyi-aware file checker",
        )

    @classmethod
    def parse_options(cls, optmanager, options, extra_args):
        """This is also brittle, only checked with flake8 3.2.1 and master."""
        if not options.no_pyi_aware_file_checker:
            checker.FileChecker = PyiAwareFileChecker

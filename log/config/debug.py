""" Debugging/info log

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2017-08-21
:Copyright: 2016, Karr Lab
:License: MIT
"""

from copy import deepcopy
import sys

import log
from . import config_log
from log.config.config_from_files_and_env import ConfigFromFilesAndEnv

class MakeLoggers(object):

    def __init__(self):
        self.loggers = None
        
    def setup_logger(self, options):
        """ Create and configure logs

        Args:
            options (:obj:`dict`): a configuration
        """

        if 'log' not in options or 'debug' not in options['log']:
            raise ValueError( """['log']['debug'] not found in options.""" )
        options = deepcopy(options['log']['debug'])
        for name, handler in options['handlers'].items():
            if handler['class'] == 'FileHandler':
                for key in handler:
                    if key not in ['class', 'filename', 'mode', 'encoding', 'errors', 'buffering']:
                        handler.pop(key)

            elif handler['class'] == 'StreamHandler':
                for key in handler:
                    if key not in ['class', 'stream']:
                        handler.pop(key)

        _, _, loggers = log.config.config_log.ConfigLog.from_dict(options)
        self.loggers = loggers
        return self


    def get_logger(self, name, loggers=None):
        """ Returns logger with name `name`. Optionally, search for logger in 
        passed in dictionary.

        Args:
            name (:obj:`str`): log name
            loggers (:obj:`dict`, optional): dictionary of loggers to search over
        """

        if loggers is None:
            loggers = self.loggers
            if loggers is None:
                raise ValueError( "No logger initialized." )

        if not isinstance(loggers, dict):
            raise ValueError( "loggers must be a dict." )

        if name not in loggers:
            raise ValueError( "logger named '{}' not found.".format(name) )
            
        return loggers[name]

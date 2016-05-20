import codecs
import syslog


class _HandlerInterface(object):
    """
    basic interface for message handlers
    """

    def __init__(self, append_new_line=True):
        """
        :param append_new_line: should a new line be appended to the message
        :type append_new_line: bool
        """
        self.append_new_line = append_new_line

    def _append_new_line(self, message):
        """appends new line to message if `new_line_appended` is True

        :param message: the message to be written
        :type message: str

        :return: the original message with optionally appended new line char
        :rtype: str
        """
        if self.append_new_line:
            message = '{message}\n'.format(message=message)
        return message

    def write(self, message):
        """writes the message to the configured endpoint

        :param message: what you want logged
        :type message: str
        """
        raise NotImplementedError


class StreamHandler(_HandlerInterface):
    """
    a handler for writing messages to a stream, i.e. STDOUT or STDERR
    """

    def __init__(self, stream, *args, **kwargs):
        """
        :param stream: stream to be written to
        :type stream: sys.

        :param append_new_line: should a new line be appended to the message
        :type append_new_line: bool
        """
        super(StreamHandler, self).__init__(*args, **kwargs)
        self.stream = stream

    def write(self, message):
        """writes the message to the configured stream

        :param message: what you want logged
        :type message: str
        """
        message = self._append_new_line(message)
        self.stream.write(message)
        self.stream.flush()


class FileHandler(_HandlerInterface):
    """
    a handler for writing messages to a file. __note:__ if you want to rotate the log files, use
    the system `logrotate` functionality - it works better than anything you can put together here.
    """

    def __init__(self, filename, mode='a', encoding='utf8', *args, **kwargs):
        """
        :param filename: the name of the file to be written to
        :type filename: str

        :param mode: the file write mode - defaults to 'a' (append)
        :type mode: str

        :param encoding: the encoding of the file - defaults to 'utf8'
        :type encoding: str

        :param append_new_line: should a new line be appended to the message
        :type append_new_line: bool
        """
        super(FileHandler, self).__init__(*args, **kwargs)
        self._filename = filename
        self._mode = mode
        self._encoding = encoding
        self.fh = codecs.open(filename, mode=mode, encoding=encoding)

    def write(self, message):
        """appends the message to the configured file

        :param message: what you want logged
        :type message: str
        """
        message = self._append_new_line(message)
        self.fh.write(message)
        self.fh.flush()


class SocketHandler(_HandlerInterface):
    """
    a handler for writing logs to a socket. this can be used for network sockets of unix sockets.
    """

    def __init__(self, socket, address, *args, **kwargs):
        """
        :param socket: a configured socket
        :type socket: socket.socket

        :param address: full connection information for the socket to bind to
        :type: address: type

        :param append_new_line: should a new line be appended to the message
        :type append_new_line: bool

        >>> import socket
        >>>
        >>> net_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        >>> net_addr = ('example.com', 9999)
        >>> net_handler = SocketHandler(net_sock, net_addr)
        >>>
        >>> unix_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        >>> unix_addr = '/tmp/log.sock'
        >>> unix_handler = SocketHandler(unix_sock, unix_addr)
        """
        super(SocketHandler, self).__init__(*args, **kwargs)
        self.socket = socket
        self._address = address
        self.socket.connect(address)

    def write(self, message):
        """writes the message to the configured socket

        :param message: what you want logged
        :type message: str
        """
        message = self._append_new_line(message)
        self.socket.sendall(bytes(message, 'utf8'))


class SysLogHandler(_HandlerInterface):
    """
    a handler for writing log entries to syslog
    """

    def __init__(self, *args, **kwargs):
        """
        :param append_new_line: should a new line be appended to the message
        :type append_new_line: bool
        """
        super(SysLogHandler, self).__init__(*args, **kwargs)

    def write(self, message, level):
        """writes the message to syslog

        :param message: what you want logged
        :type message: str

        :param level: the log level of the message
        :type level: log.levels.LogLevel
        """
        message = self._append_new_line(message)
        syslog.syslog(level.syslog_eq, message)

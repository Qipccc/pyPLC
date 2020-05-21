# -*- coding:UTF-8 -*-
import sys
import logging
import os

def create_logger(logger_name, log_file):
    '''
    Create a logger.
    The same logger object will be active all through out the python
    interpreter process.
    https://docs.python.org/2/howto/logging-cookbook.html
    Use   logger = logging.getLogger(logger_name) to obtain logging all
    through out
    '''
    # 需要添加清理日志的功能（保留日志信息 一周）
    logger = logging.getLogger(logger_name)
    # Remove the stdout handler
    logger_handlers = logger.handlers[:]
    for handler in logger_handlers:
        if handler.name == 'std_out':
            logger.removeHandler(handler)
    logger.setLevel(logging.DEBUG)
    file_h = logging.FileHandler(log_file)
    file_h.setLevel(logging.DEBUG)
    file_h.set_name('file_handler')
    terminal_h = logging.StreamHandler(sys.stdout)
    terminal_h.setLevel(logging.INFO)
    terminal_h.set_name('stdout')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    tool_formatter = logging.Formatter(' %(levelname)s - %(message)s')
    file_h.setFormatter(formatter)
    terminal_h.setFormatter(tool_formatter)
    logger.addHandler(file_h)
    logger.addHandler(terminal_h)
    return logger

def create_TempFolder(filename):
    """
    create log folder in default user path
    """
    user_path = os.path.expanduser("~")
    rpFolder = os.path.join(user_path, "roboticplus")
    if not rpFolder:
        os.mkdir(rpFolder)
    rpLogerFolder = os.path.join(rpFolder,"log")
    if not os.path.exists(rpLogerFolder):
        os.mkdir(rpLogerFolder)
    return os.path.join(rpLogerFolder, filename)
    

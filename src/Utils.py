# -*- coding:UTF-8 -*-
import sys
import logging
import os
import datetime

def create_logger(logger_name, log_file):
    '''
    Create a logger.
    The same logger object will be active all through out the python
    interpreter process.
    https://docs.python.org/2/howto/logging-cookbook.html
    Use   logger = logging.getLogger(logger_name) to obtain logging all
    through out
    '''
    # Todo需要添加清理日志的功能（保留日志信息 一周）
    logger = logging.getLogger(logger_name)
    # Remove the stdout handler
    logger_handlers = logger.handlers[:]
    for handler in logger_handlers:
        if handler.name == 'std_out':
            logger.removeHandler(handler)
    logger.setLevel(logging.INFO)

    file_h = logging.FileHandler(log_file)
    file_h.setLevel(logging.INFO)
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

def delExpireLog(path):
    list_path = os.listdir(path)
    flag = 0
    if len(list_path) > 30:
        for f in enumerate(list_path):
            #ToDo 自动识别不符合要求的文件，并进行删除，防止文件奔溃
            date = f.split('.')[0].split('_')[-1]
            year,month,day = date.split('-')
            try:
                date_num = int(year) * 10000 + int(month) * 100 + int(day)
            except:
                os.remove(os.path.join(path, f))
                continue
            if flag == 0:
                min_date = date_num
                del_f = f
                flag +=1
            else:
                if date_num < min_date:
                    min_date = date_num
                    del_f = f
        del_filepath = os.path.join(path, del_f)
        os.remove(del_filepath)
    else:
        pass

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
    current_date = str(datetime.date.today())  # 2020-05-22
    filename = filename + '_' + current_date + '.log'
    # Todo 仅保留一个的日志文件，其他可以删除
    delExpireLog(rpLogerFolder)
    return os.path.join(rpLogerFolder, filename)

def readText2Dic(fname):
    data_dict = {}
    try:
        with open(fname,'r',encoding='utf-8') as f:
            for line in f:
                t = line.split(":")
                key = int(t[0].lstrip().rstrip())
                value = t[1].split('\n')[0].lstrip().rstrip()
                data_dict.update({key:value})
    except Exception as e:
        raise e
    return data_dict

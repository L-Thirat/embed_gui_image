import logging
import datetime, time
from logging import handlers
import datetime
import os


class DailyLog(handlers.RotatingFileHandler):
    def __init__(self, basedir, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
        """The handler create logFile named self.baseFilename today"""
        self.basedir_ = basedir

        self.baseFilename = self.getBaseFilename()

        handlers.RotatingFileHandler.__init__(self, self.baseFilename, mode, maxBytes, backupCount, encoding, delay)

    def getBaseFilename(self):
        """Return logFile name string formatted to today.log.alias"""
        cur_date = datetime.date.today()
        sub_dir = "%s/%s/%s/" % (str(cur_date.year), str(cur_date.month), str(cur_date.day))
        # todo check changing date folder
        if not os.path.exists(self.basedir_ + sub_dir):
            os.makedirs(self.basedir_ + sub_dir)
        basename_ = sub_dir + "system_" + cur_date.strftime("%Y-%m-%d") + ".log"

        # if settings.DEV_DEBUG:
        #     print("LOGDIR:" + self.basedir_)
        #     print("LOGFILE:" + basename_)

        return os.path.join(self.basedir_, basename_)

    def shouldRollover(self, record):
        """Rollover happen
        1. When the logFile size is get over maxBytes.
        2. When date is changed.
        """
        return 0


def GetSystemLogger():
    """Logger config"""
    log_handler = DailyLog("log/")

    formatter = logging.Formatter('%(levelname)s %(message)s')

    formatter.converter = time.localtime  # if you want UTC time
    log_handler.setFormatter(formatter)
    logger = logging.getLogger('system')
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)

    return logger

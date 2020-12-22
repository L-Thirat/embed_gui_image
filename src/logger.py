import logging
import datetime, time
from logging import handlers
import datetime
import os


class DailyLog(handlers.RotatingFileHandler):
    def __init__(self, basedir, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
        """
        @summary:
        Set self.baseFilename to date string of today.
        The handler create logFile named self.baseFilename
        """
        self.basedir_ = basedir

        self.baseFilename = self.getBaseFilename()

        handlers.RotatingFileHandler.__init__(self, self.baseFilename, mode, maxBytes, backupCount, encoding, delay)

    def getBaseFilename(self):
        """
        @summary: Return logFile name string formatted to "today.log.alias"
        """
        basename_ = "system_" + datetime.date.today().strftime("%Y-%m-%d") + ".log"

        # if settings.DEV_DEBUG:
        #     print("LOGDIR:" + self.basedir_)
        #     print("LOGFILE:" + basename_)

        return os.path.join(self.basedir_, basename_)

    def shouldRollover(self, record):
        """
        @summary:
        Rollover happen
        1. When the logFile size is get over maxBytes.
        2. When date is changed.

        @see: BaseRotatingHandler.emit
        """
        return 0


def GetSystemLogger():
    log_handler = DailyLog("log/")

    formatter = logging.Formatter('%(levelname)s %(message)s')

    formatter.converter = time.localtime  # if you want UTC time
    log_handler.setFormatter(formatter)
    logger = logging.getLogger('system')
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)

    return logger

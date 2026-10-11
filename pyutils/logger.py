import subprocess
import enum

class LogLevel(enum.IntEnum):
    SILENCE = 0
    ERROR   = 1
    WARNING = 2
    REGULAR = 3

class Logger:
    ERROR_FLAG   = "[ERR]"
    WARNING_FLAG = "[WARN]"
    REGULAR_FLAG = "[INFO]"
    SUBPROCESS_FLAG = "[SUBPROCESS]"
    SUBPROCESS_ERR_FLAG = "[SUBPROCESS_ERR]"

    m_log_level = LogLevel.WARNING

    def __init__(self):
        raise TypeError("Don't call it")

    @classmethod
    def subprocess_print(self, result: subprocess.CompletedProcess):
        # force subprocess result print in every log level
        if result.stdout:
            print(self.SUBPROCESS_FLAG, result.stdout)
        if result.stderr:
            print(self.SUBPROCESS_ERR_FLAG, result.stderr)

    @classmethod
    def print(self, log_info: str, log_level: LogLevel=LogLevel.REGULAR):
        if not log_info: # empty string
            return 
 
        if self.m_log_level == LogLevel.SILENCE:
            return 
        
        if log_level is None or log_level == LogLevel.REGULAR:
            print(self.REGULAR_FLAG, log_info)
            return 

        flag = None
        match log_level:
            case LogLevel.WARNING:
                flag = self.WARNING_FLAG
            case LogLevel.ERROR:
                flag = self.ERROR_FLAG
            case _:
                flag = self.REGULAR_FLAG

        if self.m_log_level >= log_level:
            print(flag, log_info)
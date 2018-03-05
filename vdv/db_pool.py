import time
import concurrent.futures as ftr
import cx_Oracle

class DBSessionPool(cx_Oracle.SessionPool):
    s_executor = ftr.ThreadPoolExecutor(max_workers=1)

    def __acquire(self):
        while self.busy == self.max:
            time.sleep(1)
        return super().acquire()

    def acquire(self):
        f = self.s_executor.submit(self.__acquire)
        return f.result()

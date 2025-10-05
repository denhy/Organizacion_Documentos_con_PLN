
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtCore import QThread, pyqtSignal

class ProcessWorker(QThread):

    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    done = pyqtSignal(bool, object)  # (ok, payload|exception)

    def __init__(self, job_fn, *job_args, **job_kwargs):
        super().__init__()
        self._job_fn = job_fn
        self._job_args = job_args
        self._job_kwargs = job_kwargs

    # Callbacks que se pasan al job_fn:
    def _emit_progress(self, value):
        try:
            self.progress.emit(int(value))
        except Exception:
            self.progress.emit(0)

    def _emit_status(self, msg):
        self.status.emit(str(msg))

    def run(self):
        try:
            payload = self._job_fn(self._emit_progress, self._emit_status,
                                   *self._job_args, **self._job_kwargs)
            self.done.emit(True, payload)
        except Exception as e:
            import traceback; traceback.print_exc()
            self.done.emit(False, e)

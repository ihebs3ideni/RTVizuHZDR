import threading
from typing import Callable
class ThreadBaseException(Exception):
    """Base High level exception for errors occurung in a thread scope"""

    def __init__(self, error, message: str):
        self.error = error
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return "Error Message: %s ; @ Error source: %s" % (self.message, self.error.__repr__())

class EventLoopThread(threading.Thread):
    def __init__(self, group=None, target:Callable=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        threading.Thread.__init__(self, target=target, args=args, daemon=daemon, name=name)

    def run(self) -> None:
        """Method representing the thread's activity.

        You may override this method in a subclass. The standard run() method
        invokes the callable object passed to the object's constructor as the
        target argument, if any, with sequential and keyword arguments taken
        from the args and kwargs arguments, respectively.

        """
        try:
            if self._target:
                self._target(*self._args, **self._kwargs)
        except OSError as e:
            if self._name is not None:
                id_ = str(self._name)
            else:
                id_= str(self.native_id)
            raise ThreadBaseException(error=e, message="a runtime error happened in a this thread: %s"%(id_))
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs
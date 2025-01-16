import json
import logging
from contextlib import contextmanager
from datetime import datetime
from logging import Logger
from typing import Dict, Any, Tuple, Optional, Callable

from .context_data import ContextData
from .helpers import now, JsonObject, default_extras_factory, default_id_factory

__all__ = ['Context', 'RequestContext', 'ContextLog', 'ExtrasFactoryType']

req_logger: Logger = logging.getLogger("REQ")

# Types
ExtrasFactoryType = Optional[Callable[[], Dict[str, Any]]]


class Context:
    __TIMESTAMP_FORMAT__ = "%Y-%m-%d %H:%M:%S.%f"

    def __init__(self, ctx_type: str, ctx_id_factory: Callable[[], str] = default_id_factory,
                 extras_factory: ExtrasFactoryType = default_extras_factory):
        context_id: str = ctx_id_factory()
        self.ctx_type: str = ctx_type
        self.context_id: str = context_id
        self.start_time: datetime = now()
        self.end_time: Optional[datetime] = None
        self._data: JsonObject = {}  # Dictionary to store temporary variable and pass between different scope
        self._extras_factory = extras_factory
        self.log: 'ContextLog' = ContextLog(self)

    # @property
    # def logger(self):
    #     return get_application_logger(context_id=self.context_id)

    def get(self, key: str, default: Any = None, set_if_missing: bool = False) -> Any:
        """ Get data from Context object(_data).
        If the parameter set_if_missing is True, then call setdefault to do get or set default operation on _data
        """
        if set_if_missing:
            return self._data.setdefault(key, default)
        else:
            return self._data.get(key, default)

    def remove(self, key: str) -> None:
        """Remove the given key from Context object(_data)"""
        del self._data[key]

    def set(self, key: str, value: Any):
        self._data[key] = value
        return self

    def finalize(self) -> JsonObject:
        """ Finalize the Context object.
        1. Set the end time
        2. Stop the timer named 'ALL'
        3. Finalize the log object (It will finalize the data and timers)
        :return the summary as dictionary
        """
        if self.end_time is None:
            self.end_time = now()
        data, timers = self.log.finalize()

        return {
            'type': self.ctx_type,
            'ctxId': self.context_id,
            'startTime': self.start_time.strftime(self.__TIMESTAMP_FORMAT__),
            'endTime': self.end_time.strftime(self.__TIMESTAMP_FORMAT__),
            'data': data,
            'timers': timers,
            **self._extras_factory(),
        }


class RequestContext(Context):
    def __init__(self, request: Any, ctx_type: str = 'REQ',
                 req_id_factory: Callable[[], str] = default_id_factory,
                 ctx_id_factory: Callable[[], str] = default_id_factory,
                 extras_factory: ExtrasFactoryType = default_extras_factory):
        super(RequestContext, self).__init__(ctx_type, ctx_id_factory=ctx_id_factory, extras_factory=extras_factory)
        now_: datetime = now()
        req_id: str = req_id_factory()

        # fill required values
        self.request: Any = request
        self.request_id: req_id = req_id
        self.start_time, self.end_time = now_, None
        # self.logger = self.__get_application_logger(request_id=req_id)

        self.response: Any = None
        self.http_data: Optional[JsonObject] = None
        self.view_name = None

    def set_response(self, response: Any):
        self.response = response

    def set_http_data(self, data: JsonObject):
        self.http_data = data

    def finalize(self) -> dict:
        now_ = now()
        self.end_time = now_

        dict_to_log: JsonObject = {
            **super().finalize(),
            'reqId': self.request_id,
        }

        if self.http_data is not None:
            dict_to_log.update({
                'http': self.http_data,
            })

        data_to_log = None
        try:
            data_to_log = json.dumps(dict_to_log)
        except Exception as e:
            print(f'Error occurred while serializing the context data. Error: {e}' + str(dict_to_log))
        finally:
            if data_to_log is None:
                data_to_log = str(dict_to_log)  # NOTE: Watch error case for improvements.
                # This print data with single quotes (not valid json)
            req_logger.info(data_to_log)

        return dict_to_log


class ContextLog:
    __TIMER_KEY_ALL__: str = 'ALL'

    def __init__(self, ctx: Context):
        self._ctx: Context = ctx
        self._data: ContextData = ContextData()
        self._timers: ContextData = ContextData()
        self.start_timer(self.__TIMER_KEY_ALL__)

    def get_data(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set_data(self, key: str, value: Any) -> 'ContextLog':
        self._data.update({key: value})
        return self

    def add_data(self, key: str, value: Any) -> 'ContextLog':
        """Add the given value to given key"""
        if key not in self._data:
            self.set_data(key, value)
        else:
            if isinstance(self._data[key], list):
                self._data[key].append(value)
            else:
                self._data[key] = [self._data[key], value]
        return self

    def set_status(self, key: str, value: Any) -> 'ContextLog':
        """
        Set binary value for the given value to key
        If value is truthy value then value of the key is True
        Else, value of the key is False
        """
        return self.set_data(key, True if value else False)

    def get_status(self, key: str) -> bool:
        return True if self.get_data(key) else False

    def start_timer(self, timer_name: str, current_time: datetime = None) -> 'ContextLog':
        now_ = current_time if current_time is not None else now()
        self._timers[timer_name] = now_
        return self

    def stop_timer(self, timer_name: str, current_time: datetime = None) -> 'ContextLog':
        """Calculate timedelta and return its to milliseconds"""
        now_ = current_time if current_time is not None else now()
        self._timers[timer_name] = now_ - self._timers[timer_name]
        return self

    @contextmanager
    def timeit(self, timer_name: str):
        """This is a context manager to calculate execution time for a code block.

        Examples:
            with ctx_instance.timeit('timer1'):
               # code block
        """
        try:
            self.start_timer(timer_name)
            yield
        finally:
            self.stop_timer(timer_name)

    def finalize(self) -> Tuple[JsonObject, JsonObject]:
        self.stop_timer(self.__TIMER_KEY_ALL__)
        data: JsonObject = self._data.flat()
        timers: JsonObject = ContextData(**{k: v.total_seconds() for k, v in self._timers.items()}).flat()
        return data, timers

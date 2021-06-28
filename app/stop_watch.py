from collections import OrderedDict
import time
from typing import Optional


class StopWatch(object):
    """
    This object measures multiple elapsed times
    This object is not multi-threaded safe
    """
    def __init__(self):
        self.reset()

    def reset(self) -> None:
        """ Reset the state """
        self._elapsed_dict = OrderedDict()
        self._running = False
        self._current_start = None
        self._current_label = None

    def is_running(self) -> bool:
        """ Is the clock running? """
        return self._running

    def any_time_elapsed(self) -> bool:
        """ Do we have any elapsed time? """
        return len(self._elapsed_dict) > 0

    def start(self, label: Optional[str]=None) -> None:
        """ Start the clock """
        if self._running:
            raise ValueError('StopWatch::start(): Watch is in the running state')
        self._current_start = time.time()
        self._current_label = label
        self._running = True

    def stop(self) -> None:
        """ Stop the Clock """
        if self._running:
            self._elapsed_dict[self._current_label] = (self._current_start, time.time())
            self._running = False
            self._current_start = None

    def elapsed_time(self, label: Optional[str]=None) -> float:
        """ Elapsed time for the given label """
        elapsed_pair = self._elapsed_dict.get(label)
        if elapsed_pair is None and label is None and len(self._elapsed_dict) > 0:
            the_key = list(self._elapsed_dict.keys())[-1]
            elapsed_pair = self._elapsed_dict.get(the_key)
        elif elapsed_pair is None:
            raise ValueError('StopWatch::elapsed_time(): Cannot find elapsed time')
        return elapsed_pair[1] - elapsed_pair[0]

    def total_elapsed_time(self) -> dict:
        """ Total elapsed time """
        total_et = 0.0
        return_dict = {}
        for key, value in self._elapsed_dict.items():
            total_et += value[1] - value[0]
            return_dict[key] = value[1] - value[0]
        return_dict['TOTAL_ELAPSED'] = total_et
        return return_dict

    def pretty_elapsed_time(self) -> str:
        """ Total elapsed in a pretty formatted string """
        total_et = 0.0
        return_str = ''
        for key, value in self._elapsed_dict.items():
            total_et += value[1] - value[0]
            return_str += '{}: {}\n'.format(key, value[1] - value[0])
        return_str += 'TOTAL_ELAPSED: {}\n'.format(total_et)
        return return_str


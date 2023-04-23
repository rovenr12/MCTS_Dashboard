from dataclasses import dataclass, field
from typing import Callable, List, Union
from dash.dependencies import handle_callback_args
from dash import Input, Output, State


@dataclass
class Callback:
    func: Callable
    outputs: Union[Output, List[Output]]
    inputs: Union[Input, List[Input]]
    states: Union[State, List[State]] = field(default_factory=list)
    kwargs: dict = field(default_factory=lambda: {"prevent_initial_call": False})


class CallbackManager:
    def __init__(self, callbacks=None):
        self._callbacks = [] if not callbacks else callbacks

    def callback(self, *args, **kwargs):
        output, inputs, state, prevent_initial_call = handle_callback_args(
            args, kwargs
        )

        def wrapper(func):
            self._callbacks.append(Callback(func, output, inputs, state,
                                            {"prevent_initial_callback": prevent_initial_call}))

        return wrapper

    def get_callbacks(self):
        return self._callbacks

    def __add__(self, other):
        if self.__class__ != type(other):
            raise TypeError(f"Unable to do add operation between {type(self.__class__)} and {type(other)}. "
                            f"Only allows add operation between two CallbackManager class.")

        return CallbackManager(self._callbacks + other.get_callbacks())

    def attach_to_app(self, app):
        for callback in self._callbacks:
            app.callback(callback.outputs, callback.inputs, callback.states, **callback.kwargs)(callback.func)

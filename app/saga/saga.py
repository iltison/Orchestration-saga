from __future__ import annotations
from abc import ABC, abstractmethod

class Order:
    _state = None

    def __init__(self, state:State) -> None:
        self.set_state(state)

    def set_state(self, state:State) -> None:
        print(f"Context: Transitioning to {type(state).__name__}")
        self._state = state
        self._state.item = self

    def accept(self):
        self._state.accept()

class State(ABC):
    @abstractmethod
    def accept(self) -> None:
        pass

class AvailabilityOrderState(State):
    def accept(self):
        print("Товар в наличии")
        self.item.set_state(PaymentOrderState())

class PaymentOrderState(State):
    def accept(self):
        print("Товар оплачен")
        self.item.set_state(DeliveryOrderState())

class DeliveryOrderState(State):
    def accept(self):
        print("Товар отправлен")

item = Order(AvailabilityOrderState())
item.accept()
item.accept()
item.accept()

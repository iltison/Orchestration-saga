from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum

class OrderState(Enum):
    Availability = 'Availability'
    Payment = 'Payment'
    Delivery = 'Delivery'

class SAGA:
    _state = None

    def set_state(self, state: OrderState) -> None:
        if state == OrderState.Availability:
            self._state = AvailabilityOrderState()
        elif state == OrderState.Payment:
            self._state = PaymentOrderState()
        elif state == OrderState.Delivery:
            self._state = DeliveryOrderState()

        print(f"Context: Transitioning to {type(self._state).__name__}")
        self._state.item = self

    def get_state(self):
        return self._state


class State(ABC):
    @abstractmethod
    def accept(self) -> None:
        pass


class AvailabilityOrderState(State):
    def accept(self):
        print("Товар в наличии")
        self.item.set_state(OrderState.Payment)


class PaymentOrderState(State):
    def accept(self):
        print("Товар оплачен")
        self.item.set_state(OrderState.Delivery)


class DeliveryOrderState(State):
    def accept(self):
        print("Товар отправлен")

def main():
    item = SAGA()
    item.set_state(OrderState.Availability)
    item.get_state().accept()
    item.get_state().accept()
    item.get_state().accept()
main()
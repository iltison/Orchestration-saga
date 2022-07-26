from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum

class BookEntity:
    # TODO: работа с бд
    def __init__(self, name:str, id:int):
        self.status = None
        self.name = name
        self.id = id

    def update_order_status(self, status: OrderState):

        self.status = status
        print(f'Статус обновлен! {status}')

    def get_info(self):
        return {'id':self.id,'name':self.name}

class OrderState(Enum):
    Availability = 'Availability'
    Payment = 'Payment'
    Delivery = 'Delivery'

class SAGA:
    _state = None
    def __init__(self, book:BookEntity):
        self.book = book

    def set_state(self, state: OrderState) -> None:
        if state == OrderState.Availability:
            self._state = AvailabilityOrderState()
        elif state == OrderState.Payment:
            self._state = PaymentOrderState()
        elif state == OrderState.Delivery:
            self._state = DeliveryOrderState()
        print(f"\nContext: Transitioning to {type(self._state).__name__}")
        self._state.saga = self
        self.book.update_order_status(state)

    def get_state(self):
        return self._state


class State(ABC):
    @abstractmethod
    def accept(self) -> BookEntity:
        # TODO: отправка сообщения в rmq + проверка
        pass


class AvailabilityOrderState(State) :
    def accept(self) -> BookEntity:
        print("Товар в наличии")
        print(self.saga.book.get_info())
        print(self.saga.book.status)
        self.saga.set_state(OrderState.Payment)
        return self.saga.book

class PaymentOrderState(State):
    def accept(self) -> BookEntity:
        print("Товар оплачен")
        print(self.saga.book.status)
        self.saga.set_state(OrderState.Delivery)
        return self.saga.book


class DeliveryOrderState(State):
    def accept(self) -> BookEntity:
        print("Товар отправлен")
        print(self.saga.book.status)
        return self.saga.book

def main():
    item = SAGA(BookEntity('Hobbit',2))
    item.set_state(OrderState('Availability'))
    book = item.get_state().accept()
    book = item.get_state().accept()
    book = item.get_state().accept()
main()
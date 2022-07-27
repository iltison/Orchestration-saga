from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from app.RPC.rpc import RpcClient

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
    Cancel = 'Cancel'

class SAGA:
    def __init__(self, book:BookEntity) -> None:
        self.book = book
        self.amq = RpcClient()
        self.amq.connect()

        self.state = OrderState.Availability

    @property
    def state(self) -> State:
        return self._state

    @state.setter
    def state(self, state: OrderState) -> None:
        if state == OrderState.Availability:
            self._state = AvailabilityOrderState()
        elif state == OrderState.Payment:
            self._state = PaymentOrderState()
        elif state == OrderState.Delivery:
            self._state = DeliveryOrderState()
        elif state == OrderState.Cancel:
            self._state = CancelOrderState()
        print(f"\nContext: Transitioning to {type(self._state).__name__}")
        self._state.saga = self
        self.book.update_order_status(state)

    def accept(self) -> None:
        self._state.accept()

class State(ABC):
    @abstractmethod
    def accept(self) -> BookEntity:
        # TODO: отправка сообщения в rmq + проверка
        pass


class AvailabilityOrderState(State):
    saga=None
    def accept(self) -> BookEntity:
        res = self.saga.amq.call('Availability')
        if res == 'True':
            print("Товар в наличии")
            self.saga.state = OrderState.Payment
        else:
            self.saga.state = OrderState.Cancel
        return self.saga.accept()

class PaymentOrderState(State):
    saga = None
    def accept(self) -> BookEntity:
        res = bool(self.saga.amq.call('Delivery'))
        if res == 'True':
            print("Товар оплачен")
            self.saga.state = OrderState.Delivery
        else:
            self.saga.state = OrderState.Cancel
        return self.saga.accept()


class DeliveryOrderState(State):
    saga = None
    def accept(self) -> BookEntity:
        print("Товар отправлен")
        return self.saga.book

class CancelOrderState(State):
    def accept(self) -> None:
        print('Отмена!')

def main():
    item = SAGA(BookEntity('Hobbit',2))
    item.accept()

main()
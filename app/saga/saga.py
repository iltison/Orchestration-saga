from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from app.RPC.rpc import RpcClient

class OrderState(Enum):
    Available = 'Available'
    Payment = 'Payment'
    Delivery = 'Delivery'
    Cancel = 'Cancel'

# class RpcClient:
#     def connect(self):
#         pass
#     def call(self, n):
#         if n == 'available':
#             return {"data":{'id_book':1,'available':True}}
#         return {"data": {'id_book': 1, 'available': True}}

class Repo:
    def add(self, book:BookEntity):
        print(f'Book created {book}')

    def remove(self):
        pass

    def get_by_idx(self):
        pass

    def update_state(self, book:BookEntity):
        print(f'Status updated {book.status}')

class BookEntity:
    def __init__(self, name:str, id:int):
        self.status = OrderState.Available
        self.name = name
        self.id = id


class SAGA:
    def __init__(self, book:BookEntity) -> None:
        self.book = book
        self.amq = RpcClient()
        self.amq.connect()

        self.state = OrderState.Available

    @property
    def state(self) -> State:
        return self._state

    @state.setter
    def state(self, state: OrderState) -> None:
        if state == OrderState.Available:
            self._state = AvailableOrderState()
        elif state == OrderState.Payment:
            self._state = PaymentOrderState()
        elif state == OrderState.Delivery:
            self._state = DeliveryOrderState()
        elif state == OrderState.Cancel:
            self._state = CancelOrderState()
        print(f"\nContext: Transitioning to {type(self._state).__name__}")
        self._state.saga = self
        self.book.status = state

    def accept(self) -> BookEntity:
        return self._state.accept()

    def cancel(self) -> BookEntity:
        return self._state.cancel()

class State(ABC):
    @abstractmethod
    def accept(self) -> BookEntity:
        pass

    def cancel(self):
        pass

class AvailableOrderState(State):
    saga=None
    def accept(self) -> BookEntity:
        res = self.saga.amq.call('available')['data']['available']
        if res:
            self.saga.state = OrderState.Payment
        else:
            self.saga.state = OrderState.Cancel
        return self.saga.accept()

    def cancel(self) -> BookEntity:
        self.saga.state = OrderState.Cancel
        return self.saga.book

class PaymentOrderState(State):
    saga = None
    def accept(self):
        res = self.saga.amq.call('Delivery')['data']['available']
        if res:
            self.saga.state = OrderState.Delivery
        else:
            self.saga.state = OrderState.Cancel
        return self.saga.accept()

    def cancel(self) -> BookEntity:
        self.saga.state = OrderState.Cancel
        return self.saga.book

class DeliveryOrderState(State):
    saga = None
    def accept(self) -> BookEntity:
        return self.saga.book

    def cancel(self) -> BookEntity:
        self.saga.state = OrderState.Cancel
        return self.saga.book

class CancelOrderState(State):
    saga = None
    def accept(self) -> None:
        print('Cancel!')
        return self.saga.book

    def cancel(self) -> BookEntity:
        pass


def main():
    repo = Repo()
    book = BookEntity('Hobbit',2)
    repo.add(book)
    print(book.status)
    item = SAGA(book)
    item.accept()
    print(book.status)
    Repo().update_state(book)


if __name__ == "__main__":
    main()
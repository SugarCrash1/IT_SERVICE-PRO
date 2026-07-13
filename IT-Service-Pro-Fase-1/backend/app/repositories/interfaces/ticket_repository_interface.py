"""Contrato del repositorio de tickets."""
from abc import ABC, abstractmethod


class ITicketRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, ticket_id): ...

    @abstractmethod
    def listar(self, *args, **kwargs): ...

    @abstractmethod
    def guardar(self, ticket): ...

    @abstractmethod
    def siguiente_codigo(self) -> str: ...

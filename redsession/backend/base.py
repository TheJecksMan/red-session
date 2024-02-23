from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAsyncBackend(ABC):
    """
    Base class with asynchronous methods for implementing your own logic
    of interaction with server sessions
    """

    @abstractmethod
    async def get(self, key: str) -> dict[str, Any] | None:
        """
        Getting session data by key (session ID).

        Args:
            key (:obj:`str`): session key in storage.

        Returns:
            :obj:`~typing.Dict` if successful, :obj:`None` otherwise (**Optional**).
        """
        raise NotImplementedError()

    @abstractmethod
    async def set(
        self, key: str, value: dict[str, Any], ex: int | None = None
    ) -> bool | None:
        """
        Writing session information to storage.

        Args:
            key (:obj:`str`): new session key to write.

            value (:obj:`~typing.Dict`): dictionary that stores user information.

            ex (:obj:`int` | :obj:`None`): key expiration time. if the value is
                :obj:`None`, the key must not expire.

        Returns:
            :obj:`True` if successful, :obj:`None` otherwise (**Optional**).
        """
        raise NotImplementedError()

    @abstractmethod
    async def update(self, key: str, value: dict[str, Any]) -> bool | None:
        """
        Updating a given session without changing the lifetime of the key.

        Args:
            key (:obj:`str`): session key in storage.

            value (:obj:`~typing.Dict`): dictionary that stores user NEW information.

        Returns:
            :obj:`True` if successful, :obj:`None` otherwise (**Optional**).
        """
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, key: str) -> int | None:
        """
        Removing user data from storage, must also include a key

        Args:
            key (:obj:`str`): session key in storage.

        Returns:
            :obj:`int` if successful, :obj:`None` otherwise (**Optional**).
        """
        raise NotImplementedError()

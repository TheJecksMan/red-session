from __future__ import annotations

import secrets
from typing import Iterable, Literal

from itsdangerous import Signer
from starlette.datastructures import MutableHeaders
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .backend.base import BaseAsyncBackend


class ServerSessionMiddleware:
    """
    This class implements middleware for working with sessions on the server side.

    Args:
        app (`ASGIApp`): The ASGI application.

        backend (:class:`~redsession.backend.BaseAsyncBackend`): The backend to store
            the session data asynchronously.

        secret_key (:class:`~typing.Iterable` | :obj:`str`): A secret
            key used for signing session data. If a list of strings
            is provided, the first element will be used for signing,
            and others for verification (useful for key rotation).

        session_length (:obj:`int`, optional): Session length without hex conversion
            and without signature. Default is 16.

        name_cookie (:obj:`str`, optional): The name of the session
            cookie. Default is "s".

        max_age (:obj:`int`, optional): The maximum age of the session,
            in seconds. Default is 604800 (7 days). If set to 0 or :obj:`None`,
            the session will not expire (**Not recommended**)

        path (:obj:`str`, optional): The path for which the session
            cookie is valid. Default is "/".

        domain (:obj:`str` | :obj:`None`, optional): The domain for which the session
            cookie is valid. Default is :obj:`None`.

        same_site (:obj:`~typing.Literal["lax", "strict", "none"]`, optional): The
            SameSite attribute for the session cookie. Must be one of
            "lax", "strict", or "none". Default is "lax".

        https_only (:obj:`bool`, optional): If True, the "secure" flag will
            be added to the session cookie, making it accessible only over
            HTTPS. Default is False.
    """

    __slots__ = (
        "_app",
        "_backend",
        "_session_length",
        "_name_cookie",
        "_max_age",
        "_path",
        "_domain",
        "_security_flags",
        "signer",
    )

    def __init__(
        self,
        app: ASGIApp,
        backend: BaseAsyncBackend,
        secret_key: Iterable[str] | str,
        session_length: int = 16,
        name_cookie: str = "s",
        max_age: int | None = 604800,  # 7 days, in seconds
        path: str = "/",
        domain: str | None = None,
        same_site: Literal["lax", "strict", "none"] = "lax",
        https_only: bool = False,
    ) -> None:
        self._app = app
        self._backend = backend
        self._session_length = session_length
        self._name_cookie = name_cookie
        self._max_age = max_age
        self._path = path
        self._domain = domain
        self._security_flags = "httponly; samesite=" + same_site

        if https_only:  # Secure flag can be used with HTTPS only
            self._security_flags += "; secure"

        self.signer = Signer(secret_key, b"session.Signer")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self._app(scope, receive, send)
            return

        connection = HTTPConnection(scope)

        initial_session_was_empty = True

        # Checking for the existence of the session name in cookies
        if self._name_cookie in connection.cookies:
            # Receipt of signed key
            signer_session_id = connection.cookies[self._name_cookie]

            if self.signer.validate(signer_session_id):
                # Receiving data from the backend using part of the token
                session_id = signer_session_id.split(".")[0]
                data_session = await self._backend.get(session_id)

                if data_session is not None:
                    # Key does not exist or data has expired
                    scope["session"] = data_session
                    initial_session_was_empty = False

        if initial_session_was_empty:
            scope["session"] = {}

        async def send_wrapper(message: Message) -> None:
            if message["type"] != "http.response.start":
                await send(message)
                return

            headers = MutableHeaders(scope=message)
            cookies = None

            if scope["session"]:
                if initial_session_was_empty:
                    # If the initial session was empty, create a new identifier
                    new_session_id = secrets.token_hex(self._session_length)
                    signer_session = self.signer.sign(new_session_id).decode()
                    await self._backend.set(
                        new_session_id, scope["session"], self._max_age
                    )

                    cookies = self._create_cookie(signer_session)
                else:
                    # Update session
                    await self._backend.update(session_id, scope["session"])
            elif not initial_session_was_empty and session_id:
                # Server delete backend session
                await self._backend.delete(session_id)
                cookies = self._create_cookie(clear=True)

            if cookies:
                headers.append("Set-Cookie", cookies)
            await send(message)

        await self._app(scope, receive, send_wrapper)

    def _create_cookie(self, data: str | None = None, clear: bool = False) -> str:
        if not clear:
            cookie_value = (
                "{name}={value}; Path={path}; {domain}{max_age}{security_flags}".format(  # noqa E501
                    name=self._name_cookie,
                    value=data,
                    path=self._path,
                    max_age=f"Max-Age={self._max_age}; "
                    if self._max_age is not None
                    else "",
                    domain=f"Domain={self._domain}; "
                    if self._domain is not None
                    else "",
                    security_flags=self._security_flags,
                )
            )
            return cookie_value
        else:
            cookie_value = "{session_cookie}={data}; path={path}; {expires}{security_flags}".format(  # noqa E501
                session_cookie=self._name_cookie,
                data="null",
                path=self._path,
                expires="expires=Thu, 01 Jan 1970 00:00:00 GMT; ",
                security_flags=self._security_flags,
            )
            return cookie_value

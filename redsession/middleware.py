import os
from typing import Iterable, Literal, Optional, Union

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

    def __init__(
        self,
        app: ASGIApp,
        backend: BaseAsyncBackend,
        secret_key: Union[Iterable[str], str],
        name_cookie: str = "s",
        max_age: Optional[int] = 604800,  # 7 days, in seconds
        path: str = "/",
        domain: Optional[str] = None,
        same_site: Literal["lax", "strict", "none"] = "lax",
        https_only: bool = False,
    ) -> None:
        self.app = app
        self.backend = backend
        self.name_cookie = name_cookie
        self.max_age = max_age
        self.path = path
        self.domain = domain
        self.security_flags = "httponly; samesite=" + same_site

        if https_only:  # Secure flag can be used with HTTPS only
            self.security_flags += "; secure"

        self.signer = Signer(secret_key, b"session.Signer")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)

        initial_session_was_empty = True
        session_id = None

        # session exists or not
        if self.name_cookie in connection.cookies:
            # get data session by session_id
            signer_session_id = connection.cookies[self.name_cookie]

            if self.signer.validate(signer_session_id):
                session_id = signer_session_id.split(".")[0]
                data_session = await self.backend.get(session_id)

                if data_session is not None:
                    # key not exists
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
                    # new session
                    new_session_id = os.urandom(32).hex()
                    signer_session = self.signer.sign(new_session_id).decode()
                    await self.backend.set(
                        new_session_id, scope["session"], self.max_age
                    )

                    cookies = self._create_cookie(signer_session)
                else:
                    # update session
                    await self.backend.update(
                        session_id, scope["session"]  # type: ignore
                    )
            elif not initial_session_was_empty and session_id:
                # server delete session
                await self.backend.delete(session_id)
                cookies = self._create_cookie(clear=True)

            if cookies:
                headers.append("Set-Cookie", cookies)
            await send(message)

        await self.app(scope, receive, send_wrapper)

    def _create_cookie(self, data: Optional[str] = None, clear: bool = False) -> str:
        if not clear:
            cookie_value = "{name}={value}; Path={path}; {domain}{max_age}{security_flags}".format(  # noqa E501
                name=self.name_cookie,
                value=data,
                path=self.path,
                max_age=f"Max-Age={self.max_age}; " if self.max_age is not None else "",
                domain=f"Domain={self.domain}; " if self.domain is not None else "",
                security_flags=self.security_flags,
            )
            return cookie_value
        else:
            cookie_value = "{session_cookie}={data}; path={path}; {expires}{security_flags}".format(  # noqa E501
                session_cookie=self.name_cookie,
                data="null",
                path=self.path,
                expires="expires=Thu, 01 Jan 1970 00:00:00 GMT; ",
                security_flags=self.security_flags,
            )
            return cookie_value

Middleware
----------

.. autoclass:: redsession.ServerSessionMiddleware
    :members:
    :show-inheritance:

.. attention::

    If you want to change the session length, read the
    `OWASP Sheet Cheat <https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html>`_
    first before using it.

    It is also worth knowing that reducing the session length may cause the session to be repeated
    (in Redis does not store the session signature).


.. note::

    If you have any questions about the use of cookie settings, please refer to the
    `Mozila documentation <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie>`_


.. admonition:: Examples

    You can find examples of work here:

    :doc:`examples.fastapi`

    :doc:`examples.starlette`

Backend
-------


At the moment, the library provides only one class for interacting with Redis.

.. warning::

    Support for redis cluster is not yet available.


.. autoclass:: redsession.backend.RedisBackend
    :show-inheritance:


.. admonition:: Examples

    You can find examples of work here:

    :doc:`examples.fastapi`

    :doc:`examples.starlette`


Base class
==========

If you can implement your own logic. Just use the base class.

.. autoclass:: redsession.backend.BaseAsyncBackend
    :members:
    :undoc-members:
    :show-inheritance:

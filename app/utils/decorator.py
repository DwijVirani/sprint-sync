import inspect
from enum import Enum
from functools import wraps
from typing import (
    Any,
    Callable,
    Concatenate,
    ParamSpec,
    TypeVar,
    cast,
)
from collections.abc import Coroutine

from fastapi import HTTPException, Request

P = ParamSpec("P")
R = TypeVar("R")

# A sync function that takes (Request, *P.args, **P.kwargs) and returns R
FuncSync = Callable[Concatenate[Request, P], R]

# An async function that takes (Request, *P.args, **P.kwargs) and returns Coroutine[Any, Any, R]
FuncAsync = Callable[Concatenate[Request, P], Coroutine[Any, Any, R]]

# Our decorator can wrap either a sync or an async function
FuncUnion = FuncSync[P, R] | FuncAsync[P, R]


class Role(str, Enum):
    ADMIN = "ADMIN"
    USER = "APPROVED"


def check_roles(user_role: str, allowed_roles: list[Role]) -> None:
    user_roles = [role.lower() for role in user_role] if isinstance(user_role, list) else [user_role.lower()]
    allowed_role_values = [r.value.lower() for r in allowed_roles]
    if not any(role in allowed_role_values for role in user_roles):
        raise HTTPException(
            status_code=403,
            detail=f"Roles {user_role} not authorized to perform this action",
        )


def requires_role(roles: list[Role]) -> Callable[[FuncUnion[P, R]], FuncUnion[P, R]]:
    """
    Decorator that checks if the user's role is allowed before calling the endpoint.
    """

    def decorator(func: FuncUnion[P, R]) -> FuncUnion[P, R]:
        # We will create two separate wrappers (one async, one sync)
        # and pick the correct one at runtime.

        @wraps(func)
        async def async_wrapper(
            request: Request, *args: P.args, **kwargs: P.kwargs
        ) -> R:
            if hasattr(request.state, 'user') and request.state.user and request.state.user["role"]:
                user_role = request.state.user["role"]
                check_roles(user_role, roles)

            # Since we know this branch is only used if `func` is async,
            # cast `func` to `FuncAsync` so we can safely await it.
            func_async = cast(FuncAsync[P, R], func)
            return await func_async(request, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(request: Request, *args: P.args, **kwargs: P.kwargs) -> R:
            if hasattr(request.state, 'user') and request.state.user and request.state.user["role"]:
                user_role = request.state.user["role"]
                check_roles(user_role, roles)

            # Since we know this branch is only used if `func` is sync,
            # cast `func` to `FuncSync`.
            func_sync = cast(FuncSync[P, R], func)
            return func_sync(request, *args, **kwargs)

        # Decide at runtime which wrapper to return
        if inspect.iscoroutinefunction(func):
            return cast(FuncUnion[P, R], async_wrapper)
        else:
            return cast(FuncUnion[P, R], sync_wrapper)

    return decorator

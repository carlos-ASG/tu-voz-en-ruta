---
name: python
description: >
  Python modern patterns and best practices using type hints, dataclasses, and Protocol-based design.
  Trigger: When implementing or refactoring Python in .py files (type hints, dataclasses, protocols, enums, type guards, removing Any, tightening types).
license: Apache-2.0
metadata:
  author: Carlos
  version: "1.0"
  scope: [root]
  auto_invoke: "Writing Python types/dataclasses"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, WebFetch, WebSearch, Task
---

## Enum Pattern (REQUIRED)

```python
# ✅ ALWAYS: Use Enum for constants with type safety
from enum import Enum, auto

class Status(str, Enum):
    """String-based enum for JSON serialization."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class Priority(Enum):
    """Auto-valued enum."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()

# ❌ NEVER: Bare string literals or constants dict
STATUS_ACTIVE = "active"  # NO!
STATUS = {"ACTIVE": "active"}  # NO!
```

**Why?** Type safety, IDE autocomplete, exhaustiveness checking, prevents typos.

## Dataclasses Over Dicts (REQUIRED)

```python
# ✅ ALWAYS: Use dataclasses for structured data
from dataclasses import dataclass, field

@dataclass(frozen=True)  # Immutable by default
class UserAddress:
    street: str
    city: str
    zip_code: str
    country: str = "Mexico"  # Default value

@dataclass
class User:
    id: str
    name: str
    email: str
    address: UserAddress  # Nested dataclass
    tags: list[str] = field(default_factory=list)  # Mutable default
    created_at: str | None = None

# ❌ NEVER: Plain dicts for structured data
user = {
    "id": "123",
    "name": "Carlos",
    "address": {"street": "...", "city": "..."}  # NO!
}
```

**Why?** Type checking, validation, immutability, clear structure, IDE support.

## Type Hints (REQUIRED)

```python
# ✅ ALWAYS: Use modern type hints (Python 3.10+)
from typing import Protocol, TypeAlias
from collections.abc import Sequence, Mapping, Callable

# Modern union syntax
def process_user(user_id: str | None) -> User | None:
    pass

# Type aliases for complex types
UserId: TypeAlias = str
UserMap: TypeAlias = dict[UserId, User]

# Generic collections (no typing.List/Dict)
def filter_active(users: list[User]) -> list[User]:
    return [u for u in users if u.status == Status.ACTIVE]

# Callable types
Validator: TypeAlias = Callable[[str], bool]

def validate_email(email: str, validator: Validator) -> bool:
    return validator(email)

# ❌ NEVER: Missing type hints or old syntax
def process_user(user_id):  # NO!
    pass

from typing import List, Dict  # Deprecated since Python 3.9
def get_users() -> List[Dict]:  # NO! Use list[dict]
    pass
```

## Never Use `Any`

```python
from typing import Any, TypeVar, Protocol

# ✅ Use Protocol for structural typing
class Serializable(Protocol):
    def to_dict(self) -> dict[str, object]:
        ...

def serialize(obj: Serializable) -> str:
    return json.dumps(obj.to_dict())

# ✅ Use TypeVar for generics
T = TypeVar("T")

def first(items: Sequence[T]) -> T | None:
    return items[0] if items else None

# ✅ Use object for truly unknown types (prefer Protocol)
def log(value: object) -> None:
    print(str(value))

# ❌ NEVER
def process(data: Any) -> Any:  # NO!
    pass
```

## Protocol-Based Design (Duck Typing)

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    """Anything that can be drawn."""
    def draw(self) -> None:
        ...

@runtime_checkable
class Saveable(Protocol):
    """Anything that can be saved."""
    def save(self, path: str) -> None:
        ...

# Works with any object implementing the protocol
def render(obj: Drawable) -> None:
    obj.draw()

# Runtime checking
def process(obj: object) -> None:
    if isinstance(obj, Drawable):
        obj.draw()
```

## Type Guards

```python
from typing import TypeGuard

def is_user(value: object) -> TypeGuard[User]:
    """Type guard for User validation."""
    return (
        isinstance(value, dict)
        and "id" in value
        and "name" in value
        and isinstance(value["id"], str)
        and isinstance(value["name"], str)
    )

def process_data(data: object) -> None:
    if is_user(data):
        # Type checker knows data is User here
        print(data["name"])
```

## Pattern Matching (Python 3.10+)

```python
def process_response(response: dict[str, object]) -> str:
    match response:
        case {"status": "success", "data": data}:
            return f"Success: {data}"
        case {"status": "error", "message": msg}:
            return f"Error: {msg}"
        case _:
            return "Unknown response"

def process_user(user: User | None) -> str:
    match user:
        case User(status=Status.ACTIVE, name=name):
            return f"Active user: {name}"
        case User(status=Status.INACTIVE):
            return "Inactive user"
        case None:
            return "No user"
```

## Result Pattern (No Exceptions for Flow Control)

```python
from typing import Generic, TypeVar
from dataclasses import dataclass

T = TypeVar("T")
E = TypeVar("E")

@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

@dataclass(frozen=True)
class Err(Generic[E]):
    error: E

Result = Ok[T] | Err[E]

def divide(a: float, b: float) -> Result[float, str]:
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)

# Usage
match divide(10, 2):
    case Ok(value):
        print(f"Result: {value}")
    case Err(error):
        print(f"Error: {error}")
```

## Dataclass Validation

```python
from dataclasses import dataclass, field
from typing import Self

@dataclass(frozen=True)
class Email:
    """Value object with validation."""
    address: str
    
    def __post_init__(self) -> None:
        if "@" not in self.address:
            raise ValueError(f"Invalid email: {self.address}")
        # Use object.__setattr__ for frozen dataclasses
        object.__setattr__(self, "address", self.address.lower())
    
    @classmethod
    def create(cls, address: str) -> Self:
        """Factory method with validation."""
        return cls(address=address.strip().lower())

@dataclass
class User:
    id: str
    name: str
    email: Email
    
    def __post_init__(self) -> None:
        if len(self.name) < 2:
            raise ValueError("Name must be at least 2 characters")
```

## Import Organization

```python
# Standard library
import json
import logging
from pathlib import Path
from typing import Protocol, TypeAlias
from dataclasses import dataclass
from enum import Enum

# Django (if applicable)
from django.db import models
from django.http import HttpRequest, HttpResponse

# Third-party
import httpx
from pydantic import BaseModel

# Local
from .models import User
from .services import UserService
from .types import UserId, UserMap
```

## Modern Python Features Checklist

- ✅ Type hints on all functions and methods
- ✅ `dataclass` for DTOs and value objects
- ✅ `Enum` for constants
- ✅ `Protocol` for duck typing
- ✅ Pattern matching for complex conditionals
- ✅ `|` syntax for unions (not `Union`)
- ✅ `list[T]` not `List[T]` (Python 3.9+)
- ✅ `TypeAlias` for complex types
- ✅ `TypeGuard` for type narrowing
- ✅ `frozen=True` for immutability
- ✅ `field(default_factory=...)` for mutable defaults
- ✅ Context managers for resource management
- ✅ Decorators with proper type hints
- ✅ Functional programming patterns
- ❌ Never use `Any` (use `object` or `Protocol`)
- ❌ Never use bare `dict` for structured data
- ❌ Never use string literals for constants

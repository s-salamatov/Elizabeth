# Copilot Instructions for Elizabeth

## Project Overview
Elizabeth is a Python client library for the Armtek API, an enterprise parts supplier system. The project wraps raw HTTP responses into well-typed models and provides a service-based abstraction for user data and search operations.

## Architecture

**Core Pattern**: Layered service architecture with clear separation of concerns:
- **HTTP Layer** (`http.py`): Low-level HTTP client wrapping `httpx` with auth, timeout, and error handling
- **Service Layer** (`services/`): Domain-specific services (UserService, SearchService) that parse responses
- **Model Layer** (`models.py`): Pydantic models defining data contracts with validators for parsing flexibility
- **Client Layer** (`client.py`): Public facade combining services and providing caching

**Key Design Principle**: Response parsing is defensive—multiple field name variations (e.g., "KUNAG"/"KUNNR" for IDs) are supported to handle API inconsistencies. Use `first_value()` and `require_value()` helpers in `parsing.py` for this.

## Critical Workflows

### Running Tests
```bash
pytest                              # Run all unit tests
pytest -m "not integration"         # Exclude integration tests (require credentials)
pytest tests/test_user_service.py   # Run specific test file
```

### Code Quality
```bash
pylint src/infra/armtek_client tests  # Lint (runs in CI)
PYTHONPATH=src/infra pytest -q        # Pytest with correct import path
```

### Integration Testing
Integration tests run against real Armtek endpoints. Set environment variables and run:
```bash
ARMTEK_BASE_URL=... ARMTEK_LOGIN=... ARMTEK_PASSWORD=... \
ARMTEK_VKORG=... ARMTEK_KUNNR_RG=... ARMTEK_PIN=... \
pytest -m integration
```

## Project Conventions

### Response Handling Pattern
All Armtek responses follow a standard structure. Use `unwrap_resp()` from `base.py` to validate and extract the RESP section:
```python
raw = self._http.get("/api/endpoint")
resp = unwrap_resp(raw)  # Validates STATUS=200, raises ArmtekStatusError or ArmtekResponseFormatError
array = extract_array(resp, "ARRAY")  # Get ARRAY field, handle list/dict wrapper
```

### Flexible Field Mapping
API responses use variable field names for the same logical data. Always use multiple key options:
```python
from .parsing import first_value, require_value

# Optional field with fallbacks
short_name = first_value(data, ("SORTL", "SHORT_NAME", "SHORTNAME"))

# Required field (raises if None or empty)
id_val = require_value(data, ("KUNAG", "KUNNR"), "ID")
```

### Pydantic Models with Custom Parsing
Models use `field_validator` with `mode="before"` to parse raw API values. Example from `models.py`:
```python
@field_validator("is_default", mode="before")
@classmethod
def _bool_default(cls, value: object) -> bool:
    return parse_bool_flag(value)  # Handles "X", "1", True, etc.
```

### Exception Hierarchy
- `ArmtekError` (base)
  - `ArmtekHttpError`: Network/transport issues
  - `ArmtekStatusError`: API returned non-200 status; includes `.status` and `.messages`
  - `ArmtekResponseFormatError`: Response structure violated expectations

Services raise these for higher-level handling. Client code should catch them.

## Integration Points

### External Dependencies
- `httpx>=0.27`: HTTP client with basic auth
- `pydantic>=2`: Data validation and serialization
- `pytest>=7`: Test framework (note: integration tests marked with `@pytest.mark.integration`)

### API Endpoints
Search space is in `SearchService.search()` and `UserService` methods. Endpoint paths are hardcoded (e.g., `/api/ws_user/getUserVkorgList`). All endpoints return the standard STATUS/MESSAGES/RESP envelope.

### Caching
`ArmtekClient.get_client_structure()` implements optional vkorg-based caching (default on). Cache is instance-level in `_structure_cache` dict. New features using this pattern should follow the same signature style (keyword-only params, `with_cache=True` default).

## Testing Patterns

**Mocking Strategy**: Use `DummyHttpClient` (see `test_user_service.py`, `test_search_service.py`) with a response dict keyed by `(method, path)` tuples. This avoids external dependencies while testing service parsing logic.

**Test Coverage Expectations**:
- Normal case (valid response with all fields)
- Response variations (RESP as list vs dict, missing optional fields)
- Error cases (HTTP errors, status errors, format errors)

**Import Path**: Tests import from `armtek_client` directly (not `src.ELIZABETH...`) because `conftest.py` adds `src/infra` to `sys.path`.

## File Organization

```
src/ELIZABETH/infra/armtek_client/     # Main package
  __init__.py                          # Public API exports
  client.py                            # ArmtekClient facade
  config.py                            # ArmtekConfig dataclass
  http.py                              # HTTP transport layer
  models.py                            # Pydantic models
  parsing.py                           # Response parsing helpers
  exceptions.py                        # Exception classes
  services/
    __init__.py
    base.py                            # Common parsing (unwrap_resp, extract_array)
    user.py                            # UserService (vkorg, client structure)
    search.py                          # SearchService (search API)
```

## Code Style
- Max line length: 120 (`.pylintrc`)
- No docstrings required for simple methods (C0114/C0115/C0116 disabled in pylint)
- Type hints: Use `from __future__ import annotations` for forward refs; prefer `|` over `Union`
- Logging: Use module-level logger, log HTTP requests with method/URL/status

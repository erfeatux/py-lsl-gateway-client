# Tools for interacting with LSL in Second Life using python, asyncio and pydantic.

## ⚠ It is in the early stages of development. ⚠

## Tests

### Unit tests

- Just run pytest

```bash
pytest
```

### Integration tests

- Place the script `lsl/server.lsl` in an object in Second Life.
- Get the URL from it in the local chat.
- Run pytest with this URL in `--integration` argument

```bash
pytest --integration <url>
```

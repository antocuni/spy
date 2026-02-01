# Wasmtime + faulthandler SIGILL crash reproducer

## Bug

If `wasmtime.Engine()` is created **before** `faulthandler.enable()` is called,
then any WASM trap (e.g. `unreachable` instruction) crashes the process with
SIGILL ("Illegal instruction") instead of raising `wasmtime.Trap`.

If `faulthandler.enable()` is called **before** `wasmtime.Engine()`, everything
works correctly.

## Root cause

`wasmtime.Engine()` installs custom signal handlers (for SIGSEGV/SIGILL etc.) to
catch WASM traps and convert them to `wasmtime.Trap` exceptions.

`faulthandler.enable()` (which pytest calls automatically) overwrites those
signal handlers with Python's faulthandler, which doesn't know about wasmtime's
trap handling and just dumps the stack and kills the process.

If `faulthandler.enable()` runs first, wasmtime sees the existing handlers and
chains them properly.

## How to reproduce

### Standalone (no pytest needed)

```bash
# This CRASHES with "Illegal instruction":
python reproducer.py

# This WORKS:
python reproducer_fixed.py
```

### With pytest

```bash
# This CRASHES because conftest.py creates Engine() before pytest enables faulthandler:
python -m pytest test_wasmtrap.py -xvs

# This WORKS if you comment out ENGINE = wt.Engine() in conftest.py
```

## Wasmtime version

Tested with wasmtime 8.0.1 (Python bindings).

"""
Minimal reproducer: wasmtime.Engine() + faulthandler.enable() = SIGILL crash.

If wasmtime.Engine() is created BEFORE faulthandler.enable(), then calling a
WASM function that traps crashes with "Illegal instruction" instead of raising
wasmtime.Trap.

This is because:
  1. wasmtime.Engine() installs signal handlers for WASM traps
  2. faulthandler.enable() overwrites those signal handlers
  3. When WASM traps, Python's faulthandler catches SIGILL and kills the process

Run this script to see the crash:
    python reproducer.py
"""
import faulthandler
import wasmtime as wt

# BUG: Engine installs signal handlers, then faulthandler overwrites them
engine = wt.Engine()
faulthandler.enable()

module = wt.Module(engine, '(module (func (export "trap") unreachable))')
store = wt.Store(engine)
instance = wt.Instance(store, module, [])
trap_func = instance.exports(store).get("trap")

try:
    trap_func(store)
    print("BUG: no exception raised!")
except wt.Trap as e:
    print(f"OK: got expected Trap exception")

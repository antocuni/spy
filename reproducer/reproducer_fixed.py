"""
Same as reproducer.py but with faulthandler.enable() called BEFORE Engine().
This works correctly - the Trap is caught as a Python exception.
"""
import faulthandler
import wasmtime as wt

# FIX: enable faulthandler BEFORE creating the engine
faulthandler.enable()
engine = wt.Engine()

module = wt.Module(engine, '(module (func (export "trap") unreachable))')
store = wt.Store(engine)
instance = wt.Instance(store, module, [])
trap_func = instance.exports(store).get("trap")

try:
    trap_func(store)
    print("BUG: no exception raised!")
except wt.Trap as e:
    print(f"OK: got expected Trap exception")

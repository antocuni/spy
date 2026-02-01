"""
Pytest-based reproducer. Run with:
    python -m pytest test_wasmtrap.py -xvs

This crashes with "Illegal instruction" because conftest.py creates
wt.Engine() before pytest enables faulthandler.

Comment out ENGINE in conftest.py to see this test pass.
"""
import wasmtime as wt


def test_wasmtrap():
    engine = wt.Engine()
    module = wt.Module(engine, '(module (func (export "trap") unreachable))')
    store = wt.Store(engine)
    instance = wt.Instance(store, module, [])
    trap_func = instance.exports(store).get("trap")
    with __import__("pytest").raises(wt.Trap):
        trap_func(store)

"""
Creating wt.Engine() here (at conftest import time) triggers the bug.

pytest enables faulthandler AFTER importing conftest, so the order becomes:
  1. conftest.py import -> wt.Engine() -> installs signal handlers
  2. pytest enables faulthandler -> overwrites signal handlers
  3. test runs -> WASM trap -> SIGILL crash

Comment out the ENGINE line below to see the test pass.
"""
import wasmtime as wt

ENGINE = wt.Engine()  # Comment this out and the test passes

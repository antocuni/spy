"""
The @spy decorator: compile SPy-annotated functions to native code.

Usage example::

    from spy.decorator import spy, i32, f64

    @spy
    def add(x: i32, y: i32) -> i32:
        return x + y

    result = add(3, 4)  # calls the compiled native function via ctypes
"""
import ctypes
import inspect
import subprocess
import tempfile
import textwrap
from typing import Any, Callable

import py.path

from spy.backend.c.cbackend import CBackend
from spy.build.config import BuildConfig, CompilerConfig
from spy.fqn import FQN
from spy.vm.b import B
from spy.vm.function import W_ASTFunc
from spy.vm.modules.types import TYPES
from spy.vm.object import W_Type
from spy.vm.vm import SPyVM


class _SpyType:
    """
    Python-side marker for SPy numeric types.

    These make SPy type annotations syntactically valid in Python source
    files. The actual type resolution happens in the SPy compiler.
    """

    def __init__(self, name: str) -> None:
        self._spy_name = name

    def __repr__(self) -> str:
        return self._spy_name


# Numeric type markers importable by CPython programs using @spy.
i8 = _SpyType("i8")
u8 = _SpyType("u8")
i32 = _SpyType("i32")
u32 = _SpyType("u32")
f32 = _SpyType("f32")
f64 = _SpyType("f64")


def _w_type_to_ctypes(w_T: W_Type) -> Any:
    """Map a SPy W_Type to the corresponding ctypes type."""
    mapping: dict[W_Type, Any] = {
        B.w_i8: ctypes.c_int8,
        B.w_u8: ctypes.c_uint8,
        B.w_i32: ctypes.c_int32,
        B.w_u32: ctypes.c_uint32,
        B.w_f32: ctypes.c_float,
        B.w_f64: ctypes.c_double,
        B.w_bool: ctypes.c_bool,
        TYPES.w_NoneType: None,
    }
    if w_T not in mapping:
        raise TypeError(
            f"Unsupported type for @spy decorator: {w_T}. "
            "Only simple numeric types (i8, u8, i32, u32, f32, f64, bool) are supported."
        )
    return mapping[w_T]


def _compile_to_so(
    src: str, funcname: str, build_dir: py.path.local
) -> tuple[py.path.local, "SPyVM"]:
    """
    Compile SPy source to a native shared library (.so).

    Returns the path to the .so file and the SPyVM that was used to compile
    (needed to extract type information for ctypes).
    """
    # Write the .spy source file next to the build directory
    src_dir = build_dir.dirpath()
    spyfile = src_dir.join(f"{funcname}.spy")
    spyfile.write(src)

    # Run SPy compile pipeline: parse → redshift → C codegen
    vm = SPyVM()
    vm.path.append(str(src_dir))
    vm.import_(funcname)
    vm.redshift(error_mode="eager")

    # Generate C code into build_dir/src/
    config = BuildConfig(target="native", kind="exe", build_type="debug")
    backend = CBackend(vm, funcname, config, build_dir, dump_c=False)
    backend.cwrite()

    # Compile to a native shared library
    comp = CompilerConfig(config)
    c_src_dir = build_dir.join("src")
    sofile = build_dir.join(f"{funcname}.so")

    cflags = comp.cflags + ["-shared", "-fPIC", f"-I{c_src_dir}"]
    ldflags = comp.ldflags
    cmd = [comp.CC, *[str(f) for f in backend.cfiles], f"-o{sofile}", *cflags, *ldflags]

    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        stderr = proc.stderr.decode()
        raise RuntimeError(f"C compilation failed:\n{stderr}")

    return sofile, vm


def spy(func: Callable) -> Any:
    """
    Compile a SPy-annotated function to native code and return a ctypes callable.

    The function body must use SPy numeric types (i32, f64, etc.) for its
    parameter and return type annotations.  The source is extracted with
    inspect, compiled through the SPy pipeline to C, compiled to a native
    shared library, and loaded with ctypes.

    Example::

        @spy
        def add(x: i32, y: i32) -> i32:
            return x + y
    """
    src = textwrap.dedent(inspect.getsource(func))

    # Strip leading decorator lines so the .spy file contains only the
    # bare function definition.
    lines = src.splitlines()
    while lines and lines[0].lstrip().startswith("@"):
        lines.pop(0)
    src = "\n".join(lines)

    funcname = func.__name__

    tmpdir = py.path.local(tempfile.mkdtemp(prefix="spy_decorator_"))
    build_dir = tmpdir.join("build").ensure(dir=True)

    try:
        sofile, vm = _compile_to_so(src, funcname, build_dir)

        # Retrieve the compiled function's type from the VM
        fqn = FQN(f"{funcname}::{funcname}")
        w_func = vm.globals_w.get(fqn)
        if not isinstance(w_func, W_ASTFunc):
            raise ValueError(
                f"Could not find compiled SPy function '{funcname}'"
            )

        w_functype = w_func.w_functype

        # dlopen the shared library (the file can be removed after this;
        # the kernel keeps the mapping alive via the inode reference)
        lib = ctypes.CDLL(str(sofile))
        cfunc = lib[fqn.c_name]  # e.g. "spy_add$add"

        # Attach ctypes type information so Python performs the right
        # marshalling when the function is called.
        cfunc.restype = _w_type_to_ctypes(w_functype.w_restype)
        cfunc.argtypes = [_w_type_to_ctypes(p.w_T) for p in w_functype.params]

        return cfunc
    finally:
        tmpdir.remove(rec=True)

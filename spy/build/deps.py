import subprocess

import spy.libspy
from spy.build.config import BuildConfig


def ensure_deps(config: BuildConfig) -> None:
    """
    Build external dependencies required by the given config.
    This is a no-op if no deps are needed.
    """
    if config.gc == "bdwgc":
        ensure_bdwgc(config.target)


def ensure_bdwgc(target: str) -> None:
    deps_dir = str(spy.libspy.DEPS)
    lib_path = spy.libspy.DEPS.join("build", target, "lib", "libgc.a")
    if lib_path.check(file=True):
        return
    print(f"Building bdwgc for {target}...")
    subprocess.run(
        ["make", "-C", deps_dir, "bdwgc", f"TARGET={target}"],
        check=True,
    )

#ifndef SPY_POSIX_H
#define SPY_POSIX_H

#ifndef SPY_TARGET_WASI
#  include <sys/ioctl.h>
#endif
#include <unistd.h>

#ifndef SPY_STRUCT_posix_TerminalSize_DEFINED
#define SPY_STRUCT_posix_TerminalSize_DEFINED
typedef struct spy_posix$TerminalSize spy_posix$TerminalSize;
struct spy_posix$TerminalSize {
    int32_t columns;
    int32_t lines;
};
#endif

static inline spy_posix$TerminalSize
spy_posix$get_terminal_size(void) {
    spy_posix$TerminalSize result;

#ifndef SPY_TARGET_WASI
    struct winsize w;
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &w) == 0) {
        result.columns = w.ws_col;
        result.lines = w.ws_row;
    } else {
        result.columns = 80;
        result.lines = 24;
    }
#else
    // Fallback to default values on WASI (no terminal support)
    result.columns = 80;
    result.lines = 24;
#endif

    return result;
}

#endif /* SPY_POSIX_H */

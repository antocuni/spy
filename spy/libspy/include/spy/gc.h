#ifndef SPY_GC_H
#define SPY_GC_H

#include "spy.h"

typedef struct {
    void *p;
} spy_GcRef;

#ifdef SPY_GC_BDWGC
#include <gc.h>

static inline void
spy_gc_init(void) {
    GC_INIT();
}

static inline spy_GcRef
spy_GcAlloc(size_t size) {
    return (spy_GcRef){GC_MALLOC(size)};
}

#else

static inline void
spy_gc_init(void) {
}

static inline spy_GcRef
spy_GcAlloc(size_t size) {
    return (spy_GcRef){malloc(size)};
}

#endif /* SPY_GC_BDWGC */

#endif /* SPY_GC_H */

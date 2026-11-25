import db2, functools
C='../cache/db2/'
@functools.lru_cache(None)
def T(n, l='enUS'): return db2.read(f'{C}{n}.{l}.db2', n)


discrepancies = [('that', 'also'), ('nation', 'small'), ('mean', 'late'), ('substance', 'calculate'), ('good', 'department'), ('most', 'seem'), ('hold', 'last'), ('seem', 'even')]

def turboshtein(a, b):
    try:
        import turboshtein
        return turboshtein.levenshtein(a, b)
    except ImportError:
        return "turboshtein package not installed"

def definition(a, b):
    if a and b:
        return min(definition(a[1:], b) + 1, definition(a, b[1:]) + 1, definition(a[1:], b[1:]) + (a[0] != b[0]))
    return len(a) + len(b)

def original_myers(a, b):
    b, a = sorted([a, b], key=len)
    m = score = len(a)
    pv, mv = -1, 0 # Plus Vertical difference and Minus Vertical difference
    peq = [0] * 256
    for i in range(m): peq[ord(a[i])] |= 1 << i
    for c in b:
        eq = peq[ord(c)]
        xh = (((eq & pv) + pv) ^ pv) | eq
        ph = mv | ~(xh | pv) # Plus Horizontal difference
        xv = eq | mv
        mh = pv & xh # Minus Horizontal difference
        score += (ph >> m-1 & 1) - (mh >> m-1 & 1)
        ph = (ph << 1)
        pv = (mh << 1) | ~ (xv | ph)
        mv = ph & xv
    return score

def langner_global_init(a, b):
    b, a = sorted([a, b], key=len)
    m = score = len(a)
    pv, mv = 1 << m-1, 0
    peq = [0] * 256
    for i in range(m): peq[ord(a[i])] |= 1 << i
    for c in b:
        eq = peq[ord(c)]
        xh = (((eq & pv) + pv) ^ pv) | eq
        ph = mv | ~(xh | pv)
        xv = eq | mv
        mh = pv & xh
        score += (ph >> m-1 & 1) - (mh >> m-1 & 1)
        ph = (ph << 1)
        pv = (mh << 1) | ~ (xv | ph)
        mv = ph & xv
    return score

def langner_peq(a, b):
    b, a = sorted([a, b], key=len)
    m = score = len(a)
    pv, mv = -1, 0
    peq = [0] * 256
    for i in range(m): peq[ord(a[i])] |= 1 << m-i-1
    for c in b:
        eq = peq[ord(c)]
        xh = (((eq & pv) + pv) ^ pv) | eq
        ph = mv | ~(xh | pv)
        xv = eq | mv
        mh = pv & xh
        score += (ph >> m-1 & 1) - (mh >> m-1 & 1)
        ph = (ph << 1)
        pv = (mh << 1) | ~ (xv | ph)
        mv = ph & xv
    return score
def global_myers(a, b):
    m = score = len(a)
    pv, mv = -1, 0
    peq = [0] * 256
    for i in range(m): peq[ord(a[i])] |= 1 << i+1 # need to leave lowest bit for 0th row
    for c in b:
        eq = peq[ord(c)]
        xh = (((eq & pv) + pv) ^ pv) | eq
        ph = mv | ~(xh | pv) | 1 # set lowest bit to 1 to always increase from previous
        xv = eq | mv
        mh = pv & xh
        score += (ph >> m & 1) - (mh >> m & 1) # shift by m instead of m-1
        ph = (ph << 1)
        pv = (mh << 1) | ~ (xv | ph)
        mv = ph & xv
    return score

def optimized_hyyro(a, b):
    m = score = len(a)
    pv_mh, mv_ph = -1, 0
    peq = [0] * 256
    for i in range(m): peq[ord(a[i])] |= 1 << i+1
    for c in b:
        x = peq[ord(c)] | mv_ph
        d0 = (x & pv_mh) + pv_mh ^ pv_mh | x
        mv_ph |= 1 | ~(pv_mh | d0)
        pv_mh &= d0
        score += (mv_ph >> m & 1) - (pv_mh >> m & 1)
        mv_ph <<= 1
        pv_mh <<= 1
        pv_mh |= ~(mv_ph | x)
        mv_ph &= x
    return score
for a, b in discrepancies:
    print(a, b)
    for algo in [definition, turboshtein, original_myers, langner_global_init, langner_peq, global_myers, optimized_hyyro, ]:
        print(f'{algo.__name__}: {algo(a, b)}')
    print()
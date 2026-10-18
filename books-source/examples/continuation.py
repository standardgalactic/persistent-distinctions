"""Continuation equivalence by bounded-depth refinement.

A deterministic transition system with a state property is given; two states
are k-equivalent if they agree on the property after every word of length <= k.
Iterating the one-step refinement computes the classes (Moore's algorithm).
"""
from itertools import product

def refine(states, events, delta, prop, rounds):
    cls = {s: prop(s) for s in states}              # round 0: the property itself
    for r in range(rounds):
        sig = {s: (cls[s],) + tuple(cls[delta(s, a)] for a in events) for s in states}
        ids = {}
        new = {}
        for s in states:
            new[s] = ids.setdefault(sig[s], len(ids))
        if len(set(new.values())) == len(set(cls.values())) and r > 0:
            return new, r + 1
        cls = new
    return cls, rounds

# Example 1: bounded counter with an overdraft sink.  State: balance 0..N or 'X'
N = 8
states = list(range(N + 1)) + ['X']
def delta(s, a):
    if s == 'X':
        return 'X'
    if a == 'dep':
        return min(s + 1, N)
    return s - 1 if s > 0 else 'X'                 # withdrawing from 0 overdraws
prop = lambda s: s != 'X' and s >= 2               # "at least two units on hand"
cls, rounds = refine(states, ['dep', 'wd'], delta, prop, 20)
print("balances 0..%d plus overdrawn: %d states" % (N, len(states)))
print("classes after refinement: %d (stabilised in %d rounds)" % (len(set(cls.values())), rounds))
groups = {}
for s in states:
    groups.setdefault(cls[s], []).append(s)
for g in groups.values():
    print("  class:", g)

# Example 2: the parity family.  Two properties, one per event, four joint classes.
ps = [(i, j) for i in (0, 1) for j in (0, 1)]
def d2(s, a):
    i, j = s
    return ((i + 1) % 2, j) if a == 'a' else (i, (j + 1) % 2)
for name, pr in [("parity of a", lambda s: s[0]), ("parity of b", lambda s: s[1])]:
    c, r = refine(ps, ['a', 'b'], d2, pr, 10)
    print(name, "-> classes:", len(set(c.values())))
c, r = refine(ps, ['a', 'b'], d2, lambda s: s, 10)
print("both properties jointly -> classes:", len(set(c.values())))

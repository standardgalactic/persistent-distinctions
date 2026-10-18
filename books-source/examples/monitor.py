"""Bounded-response monitor: every request must be answered within K steps.

The monitor state is the age of the oldest unanswered request (0 = none).
We build the monitor as a deterministic automaton and minimise it by
partition refinement, checking the (K+1)-state count of the main text.
"""
K = 3
Ev = ['req', 'ack', 'idle']
states = list(range(K + 1)) + ['viol']

def delta(s, a):
    if s == 'viol':
        return 'viol'
    if a == 'ack':
        return 0                                   # an acknowledgement clears the oldest request
    age = (1 if a == 'req' else 0) if s == 0 else s + 1
    return 'viol' if age > K else age

accept = lambda s: s != 'viol'
cls = {s: accept(s) for s in states}
while True:
    sig = {s: (cls[s],) + tuple(cls[delta(s, a)] for a in Ev) for s in states}
    ids = {}
    new = {s: ids.setdefault(sig[s], len(ids)) for s in states}
    if len(set(new.values())) == len(set(cls.values())):
        cls = new
        break
    cls = new
print("monitor states (including the violation sink):", len(states))
print("minimal automaton states:", len(set(cls.values())))
def run(word):
    s = 0
    for a in word:
        s = delta(s, a)
    return s
for w in (['req', 'idle', 'idle', 'ack'], ['req', 'idle', 'idle', 'idle', 'ack'], ['req', 'req', 'ack']):
    print(' '.join(w), '->', 'violation' if run(w) == 'viol' else 'ok')

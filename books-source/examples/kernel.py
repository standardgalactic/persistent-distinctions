"""Linear-time viability kernel by the counter algorithm (Appendix C of the second volume).

System: a vehicle on positions 0..L with a charger at 0 and battery 0..B.
"""
from collections import deque

L, B = 10, 6
X = [(x, b) for x in range(L + 1) for b in range(B + 1)]

def actions(s):
    x, b = s
    out = []
    if x == 0:
        out.append(('wait', (0, B)))
    if b >= 1:
        if x > 0:
            out.append(('left', (x - 1, b - 1)))
            out.append(('stay', (x, b - 1)))
        if x < L:
            out.append(('right', (x + 1, b - 1)))
    return out

C = set(X)
alive = {}                      # (state, action) -> bool
count = {s: 0 for s in X}
preds = {s: [] for s in X}      # successor -> list of (state, action)
for s in X:
    for a, t in actions(s):
        alive[(s, a)] = t in C
        count[s] += alive[(s, a)]
        preds[t].append((s, a))
queue = deque(s for s in X if count[s] == 0)
dead = set(queue)
while queue:
    t = queue.popleft()
    for (s, a) in preds[t]:
        if alive[(s, a)]:
            alive[(s, a)] = False
            count[s] -= 1
            if count[s] == 0 and s not in dead:
                dead.add(s)
                queue.append(s)
kernel = set(X) - dead
print("states: %d, kernel: %d" % (len(X), len(kernel)))
print("kernel equals {b >= x}:", kernel == {(x, b) for (x, b) in X if b >= x})
reach, frontier = {(0, B)}, [(0, B)]
while frontier:
    s = frontier.pop()
    for a, t in actions(s):
        if t in kernel and t not in reach:
            reach.add(t); frontier.append(t)
print("positions reachable inside the kernel from (0,%d):" % B, sorted({x for x, b in reach}))

# Knapsack

## Integer Solver

Use when ciphertext is a subset sum or byte-weighted sum.

```python
from ortools.sat.python import cp_model

weights = [...]
target = ...
n = len(weights)

m = cp_model.CpModel()
x = [m.NewIntVar(0, 1, f"x{i}") for i in range(n)]
m.Add(sum(weights[i] * x[i] for i in range(n)) == target)

s = cp_model.CpSolver()
s.parameters.max_time_in_seconds = 30
s.parameters.num_search_workers = 8
assert s.Solve(m) in (cp_model.OPTIMAL, cp_model.FEASIBLE)
print([s.Value(v) for v in x])
```

## Byte Weighted Sum

Use when each output chunk consumes one bit-plane and can be recombined into one equation.

```python
from ortools.sat.python import cp_model

pub = [...]
ct = [...]
S = sum((1 << j) * c for j, c in enumerate(ct))
n = len(pub)

m = cp_model.CpModel()
x = [m.NewIntVar(0, 255, f"x{i}") for i in range(n)]
m.Add(sum(pub[i] * x[i] for i in range(n)) == S)

m.Add(x[0] == ord("C"))
m.Add(x[1] == ord("B"))
m.Add(x[2] == ord("C"))
m.Add(x[3] == ord("{"))
m.Add(x[n - 1] == ord("}"))
for i in range(4, n - 1):
    m.AddLinearConstraint(x[i], 32, 126)

s = cp_model.CpSolver()
s.parameters.max_time_in_seconds = 30
s.parameters.num_search_workers = 8
assert s.Solve(m) in (cp_model.OPTIMAL, cp_model.FEASIBLE)
print(bytes(s.Value(v) for v in x))
```


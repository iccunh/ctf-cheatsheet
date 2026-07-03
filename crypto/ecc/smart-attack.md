# Smart Attack

Attack ini bisa dipakai apabila terdapat E anomali di mana&#x20;

```
q = E.cardinality()
assert(p == q)
```

cardinality menandakan bahwa jumlah total titiknya E sama dengan p sehingga E anomalous. Pencegahannya mungkin bisa kurva standar seperti secp256k1 dan lain lain.

Paper can be found here: [https://wstein.org/edu/2010/414/projects/novotney.pdf](https://wstein.org/edu/2010/414/projects/novotney.pdf)

Sage script can be found here: [https://crypto.stackexchange.com/questions/70454/why-smarts-attack-doesnt-work-on-this-ecdlp](https://crypto.stackexchange.com/questions/70454/why-smarts-attack-doesnt-work-on-this-ecdlp)

```python
# Curve params
p = 0xa15c4fb663a578d8b2496d3151a946119ee42695e18e13e90600192b1d0abdbb6f787f90c8d102ff88e284dd4526f5f6b6c980bf88f1d0490714b67e8a2a2b77
a = 0x5e009506fcc7eff573bc960d88638fe25e76a9b6c7caeea072a27dcd1fa46abb15b7b6210cf90caba982893ee2779669bac06e267013486b22ff3e24abae2d42
b = 0x2ce7d1ca4493b0977f088f6d30d9241f8048fdea112cc385b793bce953998caae680864a7d3aa437ea3ffd1441ca3fb352b0b710bb3f053e980e503be9a7fece

g_x = 0x39f15e024d44228fd11c58a71c312fd64167c7d249d5677da0dfb4b9c3ed0f90701837a5e77b5a2b74433d7fbe027cd0c73b5aa7b300f7384521af0dc283dc6d
g_y = 0x5f3636a89167a6fbb7b7d1ad97d11c70756835b5f1273e20c06d9e022d74648ec22a3f92c378196d137c3f2027a67381be79e1c0d65cd9b61211a77a3842c8b2

a_x = 0x5aa8b5cf3124c552881ba67c14c863bb2ff30d960fe41b61123d2025cdddf0ea75e92d76326be9fb09b9a32373fc278ac8d5cf5ca83b9e517ce347c6879bef51
a_y = 0x2e3ddec1b35930b1039351b2814252186b30ce27ce15eda4351428868ae8593ab8c61c034ba10041cce205d7f7102c292f30ac5f3d2a2c2f3a463d837df070cd

b_x = 0x7f0489e4efe6905f039476db54f9b6eac654c780342169155344abc5ac90167adc6b8dabacec643cbe420abffe9760cbc3e8a2b508d24779461c19b20e242a38
b_y = 0xdd04134e747354e5b9618d8cb3f60e03a74a709d4956641b234daa8a65d43df34e18d00a59c070801178d198e8905ef670118c15b0906d3a00a662d3a2736bf

# Define curve
E = EllipticCurve(GF(p), [a, b])

# Protect against Pohlig-Hellman Algorithm
assert is_prime(E.order())

# Create generator
G = E.gens()[0]
A = E(a_x, a_y)
B = E(b_x, b_y)
A.order() == p

def SmartAttack(P,Q,p):
    E = P.curve()
    Eqp = EllipticCurve(Qp(p, 2), [ ZZ(t) + randint(0,p)*p for t in E.a_invariants() ])

    P_Qps = Eqp.lift_x(ZZ(P.xy()[0]), all=True)
    for P_Qp in P_Qps:
        if GF(p)(P_Qp.xy()[1]) == P.xy()[1]:
            break

    Q_Qps = Eqp.lift_x(ZZ(Q.xy()[0]), all=True)
    for Q_Qp in Q_Qps:
        if GF(p)(Q_Qp.xy()[1]) == Q.xy()[1]:
            break

    p_times_P = p*P_Qp
    p_times_Q = p*Q_Qp

    x_P,y_P = p_times_P.xy()
    x_Q,y_Q = p_times_Q.xy()

    phi_P = -(x_P/y_P)
    phi_Q = -(x_Q/y_Q)
    k = phi_Q/phi_P
    return ZZ(k)

nA = SmartAttack(G, A, p)

assert G * nA == A

shared_secret = (nA * B)[0]

print('Shared Secret:', shared_secret)
```

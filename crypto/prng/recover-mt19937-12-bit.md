# Recover MT19937 (12 Bit)

referensi: smiley 2025 ctf&#x20;

```
# https://gist.github.com/maple3142/1e3e81411a791f85073c3d902b0f14ef
```

```python
from random import getrandbits
from Crypto.Cipher import AES
from hashlib import sha256
danger = 624*32 # i hear you need this much.
given = []
key = ""
for _ in range(danger//20 - 16): # should be fine if im only giving u this much :3
    x = getrandbits(32)
    # we share <3
    key += str(x % 2**12)
    given.append(x >> 12)

key = key[:100]
key = sha256(key.encode()).digest()
flag = open("flag.txt", "rb").read().strip()
cipher = AES.new(key, AES.MODE_ECB)
print(given)
print(cipher.encrypt(flag + b"\x00" * (16 - len(flag) % 16)).hex())

'''
[460740, 510430, 449840, 653759, 349011, 404684, 565671, 151336, 476305, 497936, 41763, 941189, 388293, 588119, 945336, 802349, 728358, 42797, 304426, 638246, 1028695, 170118, 6618, 450537, 966644, 114144, 1015799, 431061, 242512, 361277, 929693, 876685, 667250, 286513, 855131, 227404, 1028552, 802960, 678698, 609056, 344877, 128798, 491943, 825669, 836993, 163687, 382325, 617036, 149687, 1024458, 395036, 123044, 588199, 366734, 618995, 123233, 621065, 246612, 380212, 929271, 715144, 820916, 759118, 1034076, 275722, 215204, 737922, 341367, 362282, 548568, 623808, 702486, 1043666, 427353, 20473, 176843, 767153, 826681, 334516, 761649, 198828, 523732, 955349, 496077, 582800, 315924, 571663, 114097, 288178, 369505, 416278, 690975, 333172, 964798, 170195, 453282, 650511, 949879, 22810, 627154, 93691, 67288, 574007, 704689, 833929, 545611, 215912, 553130, 16226, 60995, 830127, 386613, 405177, 596107, 657547, 500645, 566278, 404330, 569691, 901032, 622287, 199920, 546426, 346823, 387319, 176830, 903409, 767296, 61239, 872690, 479067, 375777, 1008156, 123524, 304932, 688431, 668942, 157891, 638507, 86987, 368570, 405220, 710891, 479436, 560974, 236112, 850417, 250958, 137845, 637518, 347027, 25265, 902081, 756062, 112961, 512605, 917275, 904862, 233169, 486928, 98543, 767822, 457250, 853509, 276601, 902297, 817530, 160601, 628865, 366681, 734127, 260478, 526614, 1042808, 884815, 951201, 644267, 642657, 824688, 643170, 577762, 785312, 585031, 213492, 635617, 980073, 400845, 294855, 761226, 564594, 30887, 164533, 499814, 40920, 187431, 290994, 223618, 307085, 857841, 1030076, 1021152, 433340, 670999, 76424, 564484, 698791, 846564, 456570, 269679, 200894, 92968, 596021, 792314, 570446, 818115, 62244, 311011, 234374, 520523, 160383, 727239, 528551, 457544, 72261, 999556, 250466, 351690, 788758, 657142, 134996, 64356, 108055, 898728, 145171, 466296, 699960, 578755, 482317, 1044448, 461178, 77644, 982099, 174272, 147970, 465941, 477858, 104579, 563469, 209831, 288799, 211571, 891028, 254850, 925679, 932755, 126578, 953042, 825695, 423755, 787244, 759375, 555333, 216755, 50593, 157586, 482514, 204373, 993000, 80608, 764665, 999634, 384528, 957767, 182036, 294697, 520003, 83362, 390857, 80971, 1012545, 391026, 5133, 194522, 430823, 550214, 699001, 52657, 127145, 598327, 568226, 899942, 849944, 556225, 278347, 609270, 427120, 858771, 332591, 12800, 831169, 626251, 835108, 766002, 603263, 270006, 170634, 36734, 661232, 97318, 188682, 1004591, 738182, 433599, 445596, 153587, 999913, 852616, 90814, 589942, 302888, 835884, 951769, 32939, 553223, 784938, 272637, 1008360, 870222, 258360, 59913, 119277, 893131, 530467, 342095, 940593, 413878, 939828, 783360, 634197, 403415, 287835, 791613, 683346, 844964, 1034575, 727399, 287797, 654034, 53471, 739461, 105046, 452300, 164145, 347109, 89072, 190880, 421853, 222190, 860745, 45637, 842471, 953558, 352527, 533999, 813895, 334927, 516717, 42802, 990139, 343731, 149906, 689806, 613601, 637494, 736229, 439047, 726010, 1017684, 670902, 921587, 36228, 704331, 701175, 644486, 505880, 451505, 87102, 453460, 166430, 333989, 445133, 244451, 482094, 821731, 43372, 234629, 779356, 370260, 715065, 564539, 262773, 945737, 893778, 641237, 983848, 1040291, 929548, 116904, 282961, 196142, 759790, 592158, 937947, 1017961, 562427, 902020, 81202, 223378, 719458, 802553, 535816, 453260, 1046793, 843952, 939627, 292428, 137861, 82269, 244851, 956104, 100875, 881487, 48186, 799112, 58214, 349187, 685898, 121673, 674040, 757033, 1033625, 466079, 508116, 284755, 202191, 792885, 224003, 688244, 187116, 552046, 890512, 71339, 923936, 838226, 362946, 372054, 1042319, 187051, 188258, 374678, 344775, 1021919, 842849, 809968, 47367, 526472, 511030, 122155, 176259, 565722, 33617, 909106, 303700, 357029, 642618, 21630, 206327, 697286, 316252, 143594, 966689, 262069, 78857, 371731, 986473, 61442, 247178, 677525, 156730, 668178, 50439, 576232, 701111, 756947, 85217, 222477, 323553, 665382, 272366, 791336, 989193, 1038568, 848837, 215483, 847691, 202495, 558697, 271933, 596977, 970669, 143980, 729628, 118373, 718549, 554870, 556265, 131565, 245785, 616439, 187063, 426237, 555588, 353176, 783445, 297832, 375034, 544926, 760215, 1016779, 689353, 640048, 275456, 8629, 123245, 559288, 304978, 789829, 181335, 713234, 939987, 714471, 357366, 492186, 215286, 761475, 836393, 1045012, 463670, 111387, 203578, 379209, 273225, 68165, 690416, 821522, 18320, 96543, 678620, 1008629, 722989, 1023060, 618941, 64782, 82970, 158842, 676480, 640585, 780693, 710326, 192312, 965181, 566161, 746519, 526994, 70282, 724631, 1044156, 75396, 53297, 203217, 849129, 692419, 699645, 443421, 174098, 685068, 709717, 950377, 183823, 939517, 960059, 286272, 393333, 545821, 776406, 73708, 650992, 878060, 671058, 418475, 337867, 635843, 679038, 564023, 755111, 1033770, 90351, 349166, 7439, 826001, 60722, 950275, 824860, 789057, 407624, 54378, 173426, 340667, 57529, 566283, 564292, 214923, 796815, 142450, 1035873, 210654, 534509, 88457, 110429, 224628, 102545, 956228, 472365, 722077, 383511, 186408, 40520, 398044, 191129, 57476, 416822, 188061, 216041, 969731, 11356, 112328, 1014991, 422715, 455941, 693327, 1021394, 156539, 703475, 79267, 770137, 425587, 934535, 549051, 296081, 74458, 248184, 707726, 687061, 110046, 736731, 790728, 430172, 58056, 312640, 969217, 956689, 819257, 682385, 23405, 951756, 482828, 781488, 662103, 1030684, 91234, 848083, 366663, 25160, 665051, 366842, 957310, 476440, 331029, 407367, 302672, 232105, 619847, 291493, 23091, 807587, 1039253, 339016, 328887, 124919, 787788, 726218, 1038674, 385495, 854631, 502072, 488413, 16469, 686977, 408849, 819639, 1046150, 917000, 930587, 649538, 346516, 1016021, 219552, 902102, 370687, 640324, 822138, 219019, 200164, 366380, 951625, 30743, 937030, 886654, 341625, 822226, 21377, 520981, 468636, 414197, 960807, 37352, 713145, 406475, 678393, 756049, 36787, 433198, 277161, 461337, 684585, 979789, 168634, 72884, 399095, 850964, 793808, 562419, 993586, 667227, 342278, 344519, 858740, 887797, 442587, 100072, 1030354, 548398, 852046, 5317, 191859, 245988, 15813, 600606, 262, 108497, 602709, 494330, 855311, 1030225, 979607, 122214, 946348, 788723, 48890, 992409, 128277, 371067, 731017, 52593, 1035441, 762977, 833742, 193335, 115591, 46492, 1034608, 24375, 538549, 630862, 687449, 27601, 841870, 251589, 987043, 267591, 643000, 479939, 1007837, 607330, 819765, 325882, 893262, 581491, 1023258, 537530, 508691, 292019, 302776, 909634, 567748, 872878, 878935, 416160, 884092, 610107, 87839, 984643, 349164, 632749, 61942, 163472, 708422, 847952, 1024238, 1046010, 332581, 657916, 335952, 661726, 315940, 589686, 792734, 694954, 404890, 603480, 703950, 107407, 447267, 469811, 110619, 543800, 543353, 307912, 575213, 587564, 688533, 746265, 228462, 372023, 599434, 438009, 282355, 744037, 179161, 810569, 520598, 245757, 358733, 990715, 325829, 214496, 47196, 943273, 225979, 299022, 874584, 387663, 108256, 348618, 66763, 111761, 483045, 312192, 743810, 675324, 295233, 533878, 122933, 744291, 803234, 935159, 348121, 940242, 314494, 302370, 254107, 561173, 109351, 833983, 740850, 807471, 679769, 6695, 64917, 512946, 877533, 172034, 357869, 942471, 370023, 139048, 744120, 767300, 48370, 773175, 367474, 158381, 788297, 379954, 693531, 196261, 599776, 698490, 453021, 570466, 935069, 581249, 868828, 965816, 311034, 208769, 255799, 646363, 839114, 842699, 355645, 783632, 264853, 906246, 644013, 959968, 844301, 141260, 47760, 743209, 1024058, 699185, 893651, 702841, 544876, 816304, 345500, 950088, 545485, 705316, 972089, 930117, 484894, 515648, 533391, 227812, 549779, 840799, 396226, 603829, 838531, 99857, 659667, 664066, 687482, 743635, 895338, 168574, 1016165, 673024, 366373, 991950, 523942, 657538, 1045864, 33297, 306379, 62337, 418301, 338750, 152830, 292783]
c8a6c38be0ec97bc32df34e0df6e5d7b64a1dc238b0e5019a728c2b7c8fbdab22393c7177dad868294557cc22ab5855989b7ff61b74e4beb4c5070bc0a390ab7902d347c04c33aa5ab0c5b7cb38d7898048de44e94671e78ea3c55c24031505499301fb5edbd3c2790e0d6d91afae53f4fc1f891ca48c79fcdd8ccd4fb4c874a

'''
```

```python

import ast
import random
from hashlib import sha256
from Crypto.Cipher import AES
from z3 import BitVec, LShR

# Import fungsi dari z3mt.py (pastikan file ini ada di folder yang sama)
# from z3mt import N, mt_gen_sol, pure_mt_solver
from z3 import *
import random
from contextlib import contextmanager
from time import perf_counter

# ------------------
# Start of utility functions
# credits: @y011d4
# ------------------

N = 624
M = 397
MATRIX_A = 0x9908B0DF
UPPER_MASK = 0x80000000
LOWER_MASK = 0x7FFFFFFF


def random_seed(seed):
    init_key = []
    if isinstance(seed, int):
        while seed != 0:
            init_key.append(seed % 2**32)
            seed //= 2**32
    else:
        init_key = seed
    key = init_key if len(init_key) > 0 else [0]
    keyused = len(init_key) if len(init_key) > 0 else 1
    return init_by_array(key, keyused)


def init_by_array(init_key, key_length):
    s = 19650218
    mt = [0] * N
    mt[0] = s
    for mti in range(1, N):
        if isinstance(mt[mti - 1], int):
            mt[mti] = (1812433253 * (mt[mti - 1] ^ (mt[mti - 1] >> 30)) + mti) % 2**32
        else:
            mt[mti] = 1812433253 * (mt[mti - 1] ^ LShR(mt[mti - 1], 30)) + mti
    i = 1
    j = 0
    k = N if N > key_length else key_length
    while k > 0:
        if isinstance(mt[i - 1], int):
            mt[i] = (
                (mt[i] ^ ((mt[i - 1] ^ (mt[i - 1] >> 30)) * 1664525)) + init_key[j] + j
            ) % 2**32
        else:
            mt[i] = (
                (mt[i] ^ ((mt[i - 1] ^ LShR(mt[i - 1], 30)) * 1664525))
                + init_key[j]
                + j
            )
        i += 1
        j += 1
        if i >= N:
            mt[0] = mt[N - 1]
            i = 1
        if j >= key_length:
            j = 0
        k -= 1
    for k in range(1, N)[::-1]:
        if isinstance(mt[i - 1], int):
            mt[i] = (
                (mt[i] ^ ((mt[i - 1] ^ (mt[i - 1] >> 30)) * 1566083941)) - i
            ) % 2**32
        else:
            mt[i] = (mt[i] ^ ((mt[i - 1] ^ LShR(mt[i - 1], 30)) * 1566083941)) - i
        i += 1
        if i >= N:
            mt[0] = mt[N - 1]
            i = 1
    mt[0] = 0x80000000
    return mt


def update_mt(mt):
    for i in range(N):
        x = (mt[i] & UPPER_MASK) ^ (mt[(i + 1) % N] & LOWER_MASK)
        if isinstance(x, int):
            xA = x >> 1
            if x & 1:
                xA ^= MATRIX_A
        else:
            # xA = LShR(x, 1) ^ If(x & 1 == 1, BitVecVal(MATRIX_A, 32), BitVecVal(0, 32))
            xA = LShR(x, 1)
            x0 = x & 1
            for j in range(32):
                if (MATRIX_A >> j) & 1:
                    xA ^= x0 << j
        mt[i] = mt[(i + M) % N] ^ xA


def temper(state):
    y = state
    if isinstance(y, int):
        y ^= y >> 11
    else:
        y ^= LShR(y, 11)
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    if isinstance(y, int):
        y ^= y >> 18
    else:
        y ^= LShR(y, 18)
    return y


def mt_gen(init_state, *, index=N):
    state = init_state[:]  # copy
    while True:
        index += 1
        if index >= N:
            update_mt(state)
            index = 0
        yield temper(state[index])


def mt_gen_sol(sol, init_state, *, index=N):
    state = init_state[:]  # copy
    twist = 0
    while True:
        index += 1
        if index >= N:
            # replace the new state with new symbolic variables
            # this somehow improve the performance of z3 a lot
            update_mt(state)
            next_state = [BitVec(f"__{twist}_state_{i}", 32) for i in range(N)]
            for x, y in zip(state, next_state):
                sol.add(x == y)
            state = next_state
            twist += 1
            index = 0
        yield temper(state[index])


# ------------------
# Extra functions
# ------------------


def state2seed624(state, keylen=624, lower=None):
    # modified from https://github.com/soon-haari/my-ctf-challenges/blob/main/2023-xmas-ctf/Christmas%20tree%20seedling/private/solve/ex.py
    state = list(state)  # copy

    if keylen < 624:
        raise ValueError(
            "This is very dangerous, if you really need a small seed, implement your own logic to find one."
        )

    step1_rnd = max(624, keylen)

    N = 624
    uint32_mask = 1 << 32
    final_state = state[:]
    assert state[0] == 0x80000000
    assert len(state) == N
    state[0] = state[N - 1]
    i = (1 + step1_rnd) % 623

    for k in range(N - 1):
        i = i - 1
        if i <= 0:
            i += 623
        state[i] = (
            (state[i] + i) ^ ((state[i - 1] ^ (state[i - 1] >> 30)) * 1566083941)
        ) % uint32_mask
        state[0] = state[N - 1]

    mt = state[:]

    i = (1 + step1_rnd) % 623
    if i == 0:
        i = 623

    for _ in range(623):
        mt[i] = (
            (mt[i] ^ ((mt[i - 1] ^ (mt[i - 1] >> 30)) * 0x5D588B65)) - i
        ) % uint32_mask
        i += 1
        if i >= 624:
            mt[0] = mt[623]
            i = 1

    mt[0] = 0x80000000
    try:
        assert mt == final_state
    except:
        for i in range(624):
            if mt[i] != final_state[i]:
                print(i)
        exit()

    origin_state = [0 for _ in range(N)]
    origin_state[0] = 19650218
    for i in range(1, N):
        origin_state[i] = (
            1812433253 * (origin_state[i - 1] ^ (origin_state[i - 1] >> 30)) + i
        ) % uint32_mask

    key = [0 for i in range(keylen)]

    if lower == None:
        for i in range(keylen - 623):
            key[i] = 1
    else:
        if lower.bit_length() > 32 * (keylen - 623):
            raise ValueError("Too much fixed bits")
        for i in range(keylen - 623):
            key[i] = lower % uint32_mask
            lower >>= 32

    i, j = 1, 0
    for _ in range(step1_rnd - 623):
        origin_state[i] = (
            (
                origin_state[i]
                ^ ((origin_state[i - 1] ^ (origin_state[i - 1] >> 30)) * 0x19660D)
            )
            + key[j]
            + j
        ) % uint32_mask
        i += 1
        j += 1
        if i >= 624:
            origin_state[0] = origin_state[623]
            i = 1

    for _ in range(N - 1):
        x = (
            (
                origin_state[i]
                ^ ((origin_state[i - 1] ^ (origin_state[i - 1] >> 30)) * 1664525)
            )
            + j
        ) % uint32_mask
        key[j] = (state[i] - x) % uint32_mask
        origin_state[i] = (
            (
                origin_state[i]
                ^ ((origin_state[i - 1] ^ (origin_state[i - 1] >> 30)) * 1664525)
            )
            + key[j]
            + j
        ) % uint32_mask

        i += 1
        if i == N:
            origin_state[0] = origin_state[N - 1]
            i = 1
        j += 1

    if key[-1] == 0:
        raise ValueError(
            "This seed won't work because key length doesn't match, Try setting another lower bits."
        )

    mySeed = 0
    for i in range(keylen - 1, -1, -1):
        mySeed = mySeed << 32
        mySeed += key[i]
    return mySeed


def pure_mt_solver():
    # use a solver with custom tactics that is relatively fast for MT19937
    # only use this if the involved variables only contains MT19937 state variables
    return Then("bit-blast", "sat").solver()


# ------------------
# Start of testing realted things
# ------------------


@contextmanager
def timeit(task_name):
    print(f"[-] Start - {task_name}")
    start = perf_counter()
    try:
        yield
    finally:
        end = perf_counter()
        print(f"[-] End - {task_name}")
        print(f"[-] Elapsed time: {end - start:.2f} seconds")


def test_exact_recovery(nbits):
    print(f"[-] Testing exact recovery with {nbits} bits")
    random.seed(12345)
    outputs = [random.getrandbits(nbits) for _ in range(N * 32 // nbits)]

    state = [BitVec(f"state_{i}", 32) for i in range(N)]
    sol = pure_mt_solver()
    for s, o in zip(mt_gen_sol(sol, state), outputs):
        sol.add(LShR(s, 32 - nbits) == o)
    with timeit("z3 solving"):
        assert sol.check() == sat

    m = sol.model()
    state = [m.evaluate(s).as_long() for s in state]

    random.setstate((3, tuple(state + [624]), None))
    for v in outputs:
        assert random.getrandbits(nbits) == v


def test_inexact_recovery(nitems):
    print(f"[-] Testing inexact recovery with {nitems} items")
    random.seed(12345)
    outputs = [(random.randrange(3) + 1) % 3 for _ in range(nitems)]

    state = [BitVec(f"state_{i}", 32) for i in range(N)]
    sol = pure_mt_solver()
    for s, o in zip(mt_gen_sol(sol, state), outputs):
        sol.add(LShR(s, 30) == o)
    with timeit("z3 solving"):
        assert sol.check() == sat

    m = sol.model()
    state = [m.evaluate(s).as_long() for s in state]

    random.setstate((3, tuple(state + [624]), None))
    for v in outputs:
        assert random.randrange(3) == v


def test_exact_seed_recovery():
    print(f"[-] Testing exact seed recovery")
    random.seed(0x87638763DEADBEEF)
    outputs = [random.getrandbits(32) for _ in range(N)]

    nseeds = 2
    seeds = [BitVec(f"seed_{i}", 32) for i in range(nseeds)]
    state = init_by_array(seeds, len(seeds))
    sol = Solver()
    for s, o in zip(mt_gen_sol(sol, state), outputs):
        sol.add(s == o)
    with timeit("z3 solving"):
        assert sol.check() == sat

    m = sol.model()
    seeds = [m.evaluate(s).as_long() for s in seeds]

    seed = 0
    for s in seeds[::-1]:
        seed <<= 32
        seed += s
    print(f"[-] Recovered seed: {seed:x}")

    random.seed(seed)
    for v in outputs:
        assert random.getrandbits(32) == v


def test_inexact_seed_recovery_slow(nitems):
    # ref: https://blog.maple3142.net/2022/11/13/seccon-ctf-2022-writeups/#janken-vs-kurenaif
    print(f"[-] Testing inexact seed recovery (slow) with {nitems} items")
    random.seed(12345)
    outputs = [(random.randrange(3) + 1) % 3 for _ in range(nitems)]

    nseeds = N
    seeds = [BitVec(f"seed_{i}", 32) for i in range(nseeds)]
    state = random_seed(seeds)
    sol = Solver()
    for s, o in zip(mt_gen_sol(sol, state), outputs):
        sol.add(LShR(s, 30) == o)
    with timeit("z3 solving"):
        assert sol.check() == sat

    m = sol.model()
    seeds = [m.evaluate(s).as_long() for s in seeds]

    seed = 0
    for s in seeds[::-1]:
        seed <<= 32
        seed += s
    print(f"[-] Recovered seed: {seed}")

    random.seed(seed)
    for v in outputs:
        assert random.randrange(3) == v


def test_inexact_seed_recovery_fast(nitems):
    # ref: https://blog.y011d4.com/20221113-seccon-ctf-writeup#janken-vs-kurenaif
    print(f"[-] Testing inexact seed recovery (fast) with {nitems} items")
    random.seed(12345)
    outputs = [(random.randrange(3) + 1) % 3 for _ in range(nitems)]

    # instead of solving for seed at once, we solve it in two phases
    # 1. recover the state from the outputs
    # 2. recover the seed from the state

    state = [BitVec(f"seed_{i}", 32) for i in range(N)]
    sol = pure_mt_solver()
    sol.add(state[0] == 0x80000000)  # this is really important!!!
    for s, o in zip(mt_gen_sol(sol, state), outputs):
        sol.add(LShR(s, 30) == o)
    with timeit("z3 solving first phase"):
        assert sol.check() == sat

    m = sol.model()
    state = [m.evaluate(s).as_long() for s in state]

    sol = Solver()
    nseeds = N
    seeds = [BitVec(f"seed_{i}", 32) for i in range(nseeds)]
    MT = random_seed(seeds)
    for s, o in zip(MT, state):
        sol.add(s == o)
    with timeit("z3 solving second phase"):
        assert sol.check() == sat

    m = sol.model()
    seeds = [m.evaluate(s).as_long() for s in seeds]

    seed = 0
    for s in seeds[::-1]:
        seed <<= 32
        seed += s
    print(f"[-] Recovered seed: {seed:x}")

    random.seed(seed)
    for v in outputs:
        assert random.randrange(3) == v


def test_simple_seed_recovery_624():
    rand = random.Random(3**1024)
    st = rand.getstate()[1][:-1]

    seed1 = state2seed624(st)
    print(f"[-] Recovered seed: {seed1:x}")
    r1 = random.Random(seed1)
    assert rand.getstate() == r1.getstate()

    seed2 = state2seed624(st, lower=0xDEADBEEF)
    print(f"[-] Recovered seed: {seed2:x}")
    r2 = random.Random(seed2)
    assert rand.getstate() == r2.getstate()

# 1. Baca data dari out.txt
with open('output.txt') as f:
    lines = f.read().splitlines()
# baris pertama: list MSB20, baris kedua: ciphertext hex
given = ast.literal_eval(lines[0])
cipher_hex = lines[1].strip()

# 2. Siapkan variabel simbolik untuk state[0..623]
state_vars = [BitVec(f'state_{i}', 32) for i in range(N)]

# 3. Bangun solver dengan taktik bit-blast
solver = pure_mt_solver()

# 4. Tambahkan kendala: untuk setiap output ke-i,
#    kita tahu (tempered_state >> 12) == given[i]
# for sym_s, known in zip(mt_gen_sol(solver, state_vars), given[:N]):
panjang = len(given)
for sym_s, known in zip(mt_gen_sol(solver, state_vars), given):
    solver.add(LShR(sym_s, 12) == known)

# 5. Pecahkan model Z3
assert solver.check().r == 1, "Gagal solve MT state!"
model = solver.model()

# 6. Ekstrak state riil
state = [model[v].as_long() for v in state_vars]

# 7. Inisialisasi ulang PRNG Python dengan state ini
prng = random.Random()
# setstate menerima tuple (version, state_tuple, None); index=624 artinya "minggu siap twist"
prng.setstate((3, tuple(state + [N]), None))

# 8. Rekonstruksi semua 982 nilai 32-bit asli
xs = [prng.getrandbits(32) for _ in range(len(given))]
print(xs)
# 9. Bangun kembali key desimal (lower 12 bit), potong 100 digit, hash, dan dekripsi
key_decimal = ''.join(str(x & 0xFFF) for x in xs)[:100]
key = sha256(key_decimal.encode()).digest()

cipher = AES.new(key, AES.MODE_ECB)
ct = bytes.fromhex(cipher_hex)
flag = cipher.decrypt(ct).rstrip(b'\x00')

print("Flag recovered:", flag)
```

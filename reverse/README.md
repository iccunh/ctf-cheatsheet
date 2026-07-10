# Reverse

Use the first page that matches the file type:

* Native ELF/PE: [Workflow](workflow.md), [Binary Triage](binary-triage.md), [Dynamic Analysis](dynamic-analysis.md)
* Need to skip a branch/check: [Patching](patching.md)
* Found xor/add/rol/s-box/permutation constants: [Byte Transforms](byte-transforms.md)
* Java, .NET, Android, Python, Go, Rust, Node: [Runtimes](runtimes.md)
* Constraint solver: [Z3 Solver](z3-solver.md)
* Path finding / input generation: [Symbolic Execution](symbolic-execution.md)
* Split reversible search: [Meet In The Middle](meet-in-the-middle.md)

Quick misses to check:

```text
wide strings: strings -a -el
hidden init: .init_array / constructors / signal handlers
packed code: UPX, mmap/mprotect, high entropy, tiny imports
runtime: PyInstaller, Go gopclntab, .NET, Java, Rust panic strings
inline compare: no strcmp import, byte-by-byte loop
encrypted success string: only decrypts on correct path
```

Useful links:

* [Ghidra headless helper](https://github.com/markuched13/Binary-Exploitation/blob/main/ghidra_auto.py)
* [Ghidra scripts](https://github.com/ghidraninja/ghidra_scripts/tree/master)
* [Ghidra Go renamer](https://github.com/ghidraninja/ghidra_scripts/blob/master/golang_renamer.py)
* [Stripped binary workflow with gdb](https://colej.net/how-to-reverse-engineer-stripped-binaries-easily-using-gdb)

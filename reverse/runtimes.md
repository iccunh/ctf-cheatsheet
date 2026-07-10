# Runtimes

Use this when `file` or `strings` says the challenge is not a normal C/C++ ELF.

## Python / PyInstaller

```bash
strings -a chall | rg -i 'pyinstaller|pyi-|python|PYZ'
python pyinstxtractor.py chall
find . -name '*.pyc' -o -name '*.py'
pycdc extracted/main.pyc > main.py
uncompyle6 extracted/main.pyc > main.py
```

Patch pyc magic if the decompiler complains:

```bash
python - <<'PY'
from pathlib import Path
p = Path('main.pyc')
b = bytearray(p.read_bytes())
b[:4] = bytes.fromhex('55 0d 0d 0a')  # Python 3.8 example
p.write_bytes(b)
PY
```

If decompile fails, use disassembly:

```bash
python -m dis main.pyc
```

## Java / JAR

```bash
file chall.jar
jar tf chall.jar
javap -classpath chall.jar -c -p com.pkg.Main
java -jar chall.jar
```

Decompiler options:

```bash
java -jar cfr.jar chall.jar --outputdir out
jadx -d out chall.jar
```

Search decompiled code:

```bash
rg -n 'flag|check|verify|equals|MessageDigest|Base64|Cipher|getBytes|charAt|substring' out
```

## Android

```bash
apktool d app.apk -o apk
jadx -d jadx app.apk
rg -n 'flag|check|verify|native|System.loadLibrary|Cipher|Base64|SharedPreferences' jadx apk
find apk -name '*.so'
```

Native libraries:

```bash
file apk/lib/*/*.so
rabin2 -zz apk/lib/arm64-v8a/lib*.so
```

Patch smali boolean:

```text
const/4 v0, 0x0  -> false
const/4 v0, 0x1  -> true
if-eqz / if-nez   -> branch on false/true
```

Rebuild/sign:

```bash
apktool b apk -o patched.apk
apksigner sign --ks debug.keystore patched.apk
```

## .NET

```bash
file chall.exe
strings -a chall.exe | rg -i 'mscorlib|dotnet|BSJB|dnspy'
ilspycmd -p -o out chall.exe
rg -n 'flag|check|verify|Equals|Encoding|Convert|FromBase64String|MD5|SHA|AES' out
```

Run:

```bash
dotnet chall.dll
mono chall.exe
```

Patch with dnSpy/ILSpy when the code is clean. For obfuscated code, search strings and follow references first.

## Go

```bash
strings -a chall | rg -i 'go build|gopclntab|runtime\.|main\.'
rabin2 -zz chall | rg 'main\.|flag|check|panic'
```

Ghidra helps if function names are recovered from `gopclntab`. Useful functions:

```text
main.main
main.init
runtime.memequal
runtime.slicebytetostring
runtime.concatstring
fmt.Fscan / bufio.Reader
```

Go strings are often `(ptr, len)` pairs. Watch both pointer and length in the decompiler.

## Rust

```bash
strings -a chall | rg -i 'rust|panic|unwrap|expect|begin_unwind|core::|alloc::|main'
rabin2 -s chall | rg 'main|panic|core|alloc'
```

Look for:

```text
panic messages with source paths
slice bounds checks near real logic
Iterator chains that decompile poorly
memcmp-like calls on final Vec/string
```

Do dynamic compare dumping before cleaning Rust decompiler output.

## Node / pkg / Electron

```bash
strings -a chall | rg -i 'node|pkg|snapshot|asar|electron|webpack|javascript'
```

Electron:

```bash
npx asar list app.asar
npx asar extract app.asar out
rg -n 'flag|check|verify|crypto|base64|Buffer|atob|eval' out
```

Node `pkg` often embeds JS in a snapshot. Start with strings and dynamic hooks; if source paths appear, search around them in extracted data.

## Unity

```bash
find . -iname 'Assembly-CSharp.dll' -o -iname 'global-metadata.dat' -o -iname 'GameAssembly.dll'
```

Mono Unity:

```bash
ilspycmd -p -o out Assembly-CSharp.dll
```

IL2CPP Unity:

```text
Use Il2CppDumper on GameAssembly.dll + global-metadata.dat, then load generated symbols into Ghidra/IDA.
```

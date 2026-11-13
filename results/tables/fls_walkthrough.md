| case                      |   DIO_Counter |   DTI (s) |   STIA (s) | strongest rule                 |   omega | decision   |     MD |   QP (s) |
|:--------------------------|--------------:|----------:|-----------:|:-------------------------------|--------:|:-----------|-------:|---------:|
| Attacker, ARI = 1 s       |            30 |      1    |       0    | R1 H/L/L -> malicious (1.00)   |  0.8333 | suspicious |   1.82 |     54.5 |
| Attacker, ARI = 2 s       |            15 |      2    |       0    | R1 H/L/L -> malicious (1.00)   |  0.8333 | suspicious |   1.82 |     54.5 |
| Attacker, ARI = 8 s       |             4 |      8    |       0    | R13 M/M/L -> quarantine (0.71) |  0.5588 | suspicious |   4.86 |    145.8 |
| Legitimate, steady state  |             1 |     30    |       0    | R25 L/H/L -> normal (1.00)     |  0.1667 | normal     | nan    |    nan   |
| Legitimate, Trickle reset |             3 |     14.97 |      13.01 | R23 L/M/M -> normal (0.67)     |  0.1667 | normal     | nan    |    nan   |

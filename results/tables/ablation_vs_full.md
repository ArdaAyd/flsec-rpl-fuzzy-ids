|   n_sensors | mobile   | method             | metric                        |   reference |     value |   difference |   p_value |   pairs |
|------------:|:---------|:-------------------|:------------------------------|------------:|----------:|-------------:|----------:|--------:|
|          16 | False    | no STIA            | accuracy                      |      0.9964 |    0.9129 |      -0.0835 |    0      |     125 |
|          16 | False    | no STIA            | f1                            |      0.9937 |    0.8537 |      -0.14   |    0      |     125 |
|          16 | False    | no STIA            | precision                     |      0.9891 |    0.7833 |      -0.2059 |    0      |     125 |
|          16 | False    | no STIA            | recall                        |      1      |    1      |       0      |    1      |     125 |
|          16 | False    | no STIA            | fpr                           |      0.0057 |    0.1162 |       0.1105 |    0      |     125 |
|          16 | False    | no STIA            | ftd_mean                      |     57.3737 |   30      |     -27.3737 |    0      |     125 |
|          16 | False    | no STIA            | time_to_block_mean            |    122.886  |   94.8414 |     -28.0443 |    0      |     125 |
|          16 | False    | no STIA            | node_legit_blocked            |      0.072  |    1.432  |       1.36   |    0      |     125 |
|          16 | False    | no STIA            | attack_dio_processed_per_node |    141.706  |  103.195  |     -38.5115 |    0      |     125 |
|          16 | False    | no RDT flag        | accuracy                      |      0.9964 |    0.9949 |      -0.0015 |    0.7049 |     125 |
|          16 | False    | no RDT flag        | f1                            |      0.9937 |    0.9913 |      -0.0025 |    0.5859 |     125 |
|          16 | False    | no RDT flag        | precision                     |      0.9891 |    0.9853 |      -0.0038 |    0.5859 |     125 |
|          16 | False    | no RDT flag        | recall                        |      1      |    1      |       0      |    1      |     125 |
|          16 | False    | no RDT flag        | fpr                           |      0.0057 |    0.0071 |       0.0014 |    0.8313 |     125 |
|          16 | False    | no RDT flag        | ftd_mean                      |     57.3737 |   57.7831 |       0.4094 |    0.3019 |     125 |
|          16 | False    | no RDT flag        | time_to_block_mean            |    122.886  |  123.005  |       0.1197 |    0.864  |     125 |
|          16 | False    | no RDT flag        | node_legit_blocked            |      0.072  |    0.096  |       0.024  |    0.5436 |     125 |
|          16 | False    | no RDT flag        | attack_dio_processed_per_node |    141.706  |  142.086  |       0.3794 |    0.5236 |     125 |
|          16 | False    | no validation      | accuracy                      |      0.9964 |    0.848  |      -0.1484 |    0      |     125 |
|          16 | False    | no validation      | f1                            |      0.9937 |    0.7948 |      -0.1989 |    0      |     125 |
|          16 | False    | no validation      | precision                     |      0.9891 |    0.6978 |      -0.2914 |    0      |     125 |
|          16 | False    | no validation      | recall                        |      1      |    1      |       0      |    1      |     125 |
|          16 | False    | no validation      | fpr                           |      0.0057 |    0.226  |       0.2203 |    0      |     125 |
|          16 | False    | no validation      | ftd_mean                      |     57.3737 |   57.3394 |      -0.0343 |    0.3173 |     125 |
|          16 | False    | no validation      | time_to_block_mean            |    122.886  |   57.3394 |     -65.5463 |    0      |     125 |
|          16 | False    | no validation      | node_legit_blocked            |      0.072  |    2.744  |       2.672  |    0      |     125 |
|          16 | False    | no validation      | attack_dio_processed_per_node |    141.706  |   82.1683 |     -59.5381 |    0      |     125 |
|          16 | False    | fixed MD = 3       | accuracy                      |      0.9964 |    0.9964 |       0      |    0.9721 |     125 |
|          16 | False    | fixed MD = 3       | f1                            |      0.9937 |    0.9916 |      -0.0021 |    1      |     125 |
|          16 | False    | fixed MD = 3       | precision                     |      0.9891 |    0.9866 |      -0.0025 |    1      |     125 |
|          16 | False    | fixed MD = 3       | recall                        |      1      |    1      |       0      |    1      |     125 |
|          16 | False    | fixed MD = 3       | fpr                           |      0.0057 |    0.0052 |      -0.0005 |    0.8068 |     125 |
|          16 | False    | fixed MD = 3       | ftd_mean                      |     57.3737 |   57.3737 |       0      |    1      |     125 |
|          16 | False    | fixed MD = 3       | time_to_block_mean            |    122.886  |  117.776  |      -5.1097 |    0.4805 |     125 |
|          16 | False    | fixed MD = 3       | node_legit_blocked            |      0.072  |    0.064  |      -0.008  |    0.7963 |     125 |
|          16 | False    | fixed MD = 3       | attack_dio_processed_per_node |    141.706  |  162.369  |      20.6631 |    0.0117 |     125 |
|          16 | False    | STIA within window | accuracy                      |      0.9964 |    0.9117 |      -0.0846 |    0      |     125 |
|          16 | False    | STIA within window | f1                            |      0.9937 |    0.8514 |      -0.1424 |    0      |     125 |
|          16 | False    | STIA within window | precision                     |      0.9891 |    0.7784 |      -0.2108 |    0      |     125 |
|          16 | False    | STIA within window | recall                        |      1      |    1      |       0      |    1      |     125 |
|          16 | False    | STIA within window | fpr                           |      0.0057 |    0.1188 |       0.1131 |    0      |     125 |
|          16 | False    | STIA within window | ftd_mean                      |     57.3737 |   30      |     -27.3737 |    0      |     125 |
|          16 | False    | STIA within window | time_to_block_mean            |    122.886  |   94.8414 |     -28.0443 |    0      |     125 |
|          16 | False    | STIA within window | node_legit_blocked            |      0.072  |    1.448  |       1.376  |    0      |     125 |
|          16 | False    | STIA within window | attack_dio_processed_per_node |    141.706  |  103.424  |     -38.2822 |    0      |     125 |
|          16 | False    | STIA persistent    | accuracy                      |      0.9964 |    0.9993 |       0.0029 |    0.0298 |     125 |
|          16 | False    | STIA persistent    | f1                            |      0.9937 |    0.9994 |       0.0057 |    0.0172 |     125 |
|          16 | False    | STIA persistent    | precision                     |      0.9891 |    0.9989 |       0.0097 |    0.0172 |     125 |
|          16 | False    | STIA persistent    | recall                        |      1      |    1      |       0      |    1      |     125 |
|          16 | False    | STIA persistent    | fpr                           |      0.0057 |    0.0015 |      -0.0042 |    0.0584 |     125 |
|          16 | False    | STIA persistent    | ftd_mean                      |     57.3737 |   85.2651 |      27.8914 |    0      |     125 |
|          16 | False    | STIA persistent    | time_to_block_mean            |    122.886  |  150.153  |      27.2669 |    0      |     125 |
|          16 | False    | STIA persistent    | node_legit_blocked            |      0.072  |    0.008  |      -0.064  |    0.0114 |     125 |
|          16 | False    | STIA persistent    | attack_dio_processed_per_node |    141.706  |  159.43   |      17.7241 |    0      |     125 |
|          16 | False    | Mamdani COG        | accuracy                      |      0.9964 |    0.9939 |      -0.0025 |    0.6415 |     125 |
|          16 | False    | Mamdani COG        | f1                            |      0.9937 |    0.9856 |      -0.0081 |    0.2886 |     125 |
|          16 | False    | Mamdani COG        | precision                     |      0.9891 |    0.9779 |      -0.0113 |    0.365  |     125 |
|          16 | False    | Mamdani COG        | recall                        |      1      |    1      |       0      |    1      |     125 |
|          16 | False    | Mamdani COG        | fpr                           |      0.0057 |    0.0077 |       0.002  |    0.9587 |     125 |
|          16 | False    | Mamdani COG        | ftd_mean                      |     57.3737 |   54.3149 |      -3.0589 |    0.0001 |     125 |
|          16 | False    | Mamdani COG        | time_to_block_mean            |    122.886  |  133.008  |      10.1223 |    0      |     125 |
|          16 | False    | Mamdani COG        | node_legit_blocked            |      0.072  |    0.096  |       0.024  |    0.6374 |     125 |
|          16 | False    | Mamdani COG        | attack_dio_processed_per_node |    141.706  |  143.686  |       1.9794 |    0.0125 |     125 |
|          16 | True     | no STIA            | accuracy                      |      0.8866 |    0.4689 |      -0.4177 |    0      |     125 |
|          16 | True     | no STIA            | f1                            |      0.8191 |    0.5091 |      -0.31   |    0      |     125 |
|          16 | True     | no STIA            | precision                     |      0.7458 |    0.3624 |      -0.3834 |    0      |     125 |
|          16 | True     | no STIA            | recall                        |      0.9536 |    0.9918 |       0.0382 |    0      |     125 |
|          16 | True     | no STIA            | fpr                           |      0.1377 |    0.7438 |       0.6062 |    0      |     125 |
|          16 | True     | no STIA            | ftd_mean                      |     36.952  |   30.54   |      -6.412  |    0      |     125 |
|          16 | True     | no STIA            | time_to_block_mean            |    146.488  |  109.17   |     -37.318  |    0      |     125 |
|          16 | True     | no STIA            | node_legit_blocked            |      6.712  |   11.568  |       4.856  |    0      |     125 |
|          16 | True     | no STIA            | attack_dio_processed_per_node |    607.987  |  355.246  |    -252.741  |    0      |     125 |
|          16 | True     | no RDT flag        | accuracy                      |      0.8866 |    0.8524 |      -0.0343 |    0      |     125 |
|          16 | True     | no RDT flag        | f1                            |      0.8191 |    0.7787 |      -0.0404 |    0      |     125 |
|          16 | True     | no RDT flag        | precision                     |      0.7458 |    0.6889 |      -0.0569 |    0      |     125 |
|          16 | True     | no RDT flag        | recall                        |      0.9536 |    0.9538 |       0.0002 |    0.743  |     125 |
|          16 | True     | no RDT flag        | fpr                           |      0.1377 |    0.1853 |       0.0476 |    0      |     125 |
|          16 | True     | no RDT flag        | ftd_mean                      |     36.952  |   35.492  |      -1.46   |    0.1372 |     125 |
|          16 | True     | no RDT flag        | time_to_block_mean            |    146.488  |  147.002  |       0.514  |    0.6668 |     125 |
|          16 | True     | no RDT flag        | node_legit_blocked            |      6.712  |    7.928  |       1.216  |    0      |     125 |
|          16 | True     | no RDT flag        | attack_dio_processed_per_node |    607.987  |  606.433  |      -1.5542 |    0.0355 |     125 |
|          16 | True     | no validation      | accuracy                      |      0.8866 |    0.406  |      -0.4806 |    0      |     125 |
|          16 | True     | no validation      | f1                            |      0.8191 |    0.4838 |      -0.3354 |    0      |     125 |
|          16 | True     | no validation      | precision                     |      0.7458 |    0.3358 |      -0.4099 |    0      |     125 |
|          16 | True     | no validation      | recall                        |      0.9536 |    0.9996 |       0.0461 |    0      |     125 |
|          16 | True     | no validation      | fpr                           |      0.1377 |    0.8423 |       0.7046 |    0      |     125 |
|          16 | True     | no validation      | ftd_mean                      |     36.952  |   37.042  |       0.09   |    0.1797 |     125 |
|          16 | True     | no validation      | time_to_block_mean            |    146.488  |   37.042  |    -109.446  |    0      |     125 |
|          16 | True     | no validation      | node_legit_blocked            |      6.712  |   11.224  |       4.512  |    0      |     125 |
|          16 | True     | no validation      | attack_dio_processed_per_node |    607.987  |  274.511  |    -333.476  |    0      |     125 |
|          16 | True     | fixed MD = 3       | accuracy                      |      0.8866 |    0.8773 |      -0.0093 |    0.0038 |     125 |
|          16 | True     | fixed MD = 3       | f1                            |      0.8191 |    0.8088 |      -0.0104 |    0.0526 |     125 |
|          16 | True     | fixed MD = 3       | precision                     |      0.7458 |    0.7183 |      -0.0274 |    0      |     125 |
|          16 | True     | fixed MD = 3       | recall                        |      0.9536 |    0.9774 |       0.0238 |    0      |     125 |
|          16 | True     | fixed MD = 3       | fpr                           |      0.1377 |    0.1602 |       0.0225 |    0      |     125 |
|          16 | True     | fixed MD = 3       | ftd_mean                      |     36.952  |   36.952  |       0      |    1      |     125 |
|          16 | True     | fixed MD = 3       | time_to_block_mean            |    146.488  |  121.242  |     -25.246  |    0.0003 |     125 |
|          16 | True     | fixed MD = 3       | node_legit_blocked            |      6.712  |    7.28   |       0.568  |    0.0008 |     125 |
|          16 | True     | fixed MD = 3       | attack_dio_processed_per_node |    607.987  |  706.929  |      98.9424 |    0.0106 |     125 |
|          16 | True     | STIA within window | accuracy                      |      0.8866 |    0.4831 |      -0.4035 |    0      |     125 |
|          16 | True     | STIA within window | f1                            |      0.8191 |    0.5153 |      -0.3038 |    0      |     125 |
|          16 | True     | STIA within window | precision                     |      0.7458 |    0.3683 |      -0.3775 |    0      |     125 |
|          16 | True     | STIA within window | recall                        |      0.9536 |    0.9919 |       0.0384 |    0      |     125 |
|          16 | True     | STIA within window | fpr                           |      0.1377 |    0.7242 |       0.5865 |    0      |     125 |
|          16 | True     | STIA within window | ftd_mean                      |     36.952  |   30.588  |      -6.364  |    0      |     125 |
|          16 | True     | STIA within window | time_to_block_mean            |    146.488  |  109.98   |     -36.508  |    0      |     125 |
|          16 | True     | STIA within window | node_legit_blocked            |      6.712  |   11.536  |       4.824  |    0      |     125 |
|          16 | True     | STIA within window | attack_dio_processed_per_node |    607.987  |  357.4    |    -250.587  |    0      |     125 |
|          16 | True     | STIA persistent    | accuracy                      |      0.8866 |    0.9218 |       0.0352 |    0      |     125 |
|          16 | True     | STIA persistent    | f1                            |      0.8191 |    0.8584 |       0.0393 |    0      |     125 |
|          16 | True     | STIA persistent    | precision                     |      0.7458 |    0.8358 |       0.09   |    0      |     125 |
|          16 | True     | STIA persistent    | recall                        |      0.9536 |    0.9067 |      -0.0469 |    0      |     125 |
|          16 | True     | STIA persistent    | fpr                           |      0.1377 |    0.0708 |      -0.0669 |    0      |     125 |
|          16 | True     | STIA persistent    | ftd_mean                      |     36.952  |  101.386  |      64.434  |    0      |     125 |
|          16 | True     | STIA persistent    | time_to_block_mean            |    146.488  |  237.84   |      91.352  |    0      |     125 |
|          16 | True     | STIA persistent    | node_legit_blocked            |      6.712  |    4.624  |      -2.088  |    0      |     125 |
|          16 | True     | STIA persistent    | attack_dio_processed_per_node |    607.987  |  575.166  |     -32.8213 |    0.1635 |     125 |
|          16 | True     | Mamdani COG        | accuracy                      |      0.8866 |    0.8385 |      -0.0482 |    0      |     125 |
|          16 | True     | Mamdani COG        | f1                            |      0.8191 |    0.7647 |      -0.0545 |    0      |     125 |
|          16 | True     | Mamdani COG        | precision                     |      0.7458 |    0.6637 |      -0.0821 |    0      |     125 |
|          16 | True     | Mamdani COG        | recall                        |      0.9536 |    0.9684 |       0.0148 |    0      |     125 |
|          16 | True     | Mamdani COG        | fpr                           |      0.1377 |    0.2103 |       0.0726 |    0      |     125 |
|          16 | True     | Mamdani COG        | ftd_mean                      |     36.952  |   35.82   |      -1.132  |    0.0056 |     125 |
|          16 | True     | Mamdani COG        | time_to_block_mean            |    146.488  |  163.782  |      17.294  |    0      |     125 |
|          16 | True     | Mamdani COG        | node_legit_blocked            |      6.712  |    8.32   |       1.608  |    0      |     125 |
|          16 | True     | Mamdani COG        | attack_dio_processed_per_node |    607.987  |  565.71   |     -42.2764 |    0      |     125 |
|          32 | False    | no STIA            | accuracy                      |      1      |    0.9948 |      -0.0052 |    0.0004 |     125 |
|          32 | False    | no STIA            | f1                            |      1      |    0.99   |      -0.01   |    0.0004 |     125 |
|          32 | False    | no STIA            | precision                     |      1      |    0.9829 |      -0.0171 |    0.0004 |     125 |
|          32 | False    | no STIA            | recall                        |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | no STIA            | fpr                           |      0      |    0.0079 |       0.0079 |    0.0004 |     125 |
|          32 | False    | no STIA            | ftd_mean                      |     59.2928 |   30      |     -29.2928 |    0      |     125 |
|          32 | False    | no STIA            | time_to_block_mean            |    122.186  |   93.0781 |     -29.1082 |    0      |     125 |
|          32 | False    | no STIA            | node_legit_blocked            |      0      |    0.24   |       0.24   |    0.0003 |     125 |
|          32 | False    | no STIA            | attack_dio_processed_per_node |    322.749  |  231.988  |     -90.761  |    0      |     125 |
|          32 | False    | no RDT flag        | accuracy                      |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | no RDT flag        | f1                            |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | no RDT flag        | precision                     |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | no RDT flag        | recall                        |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | no RDT flag        | fpr                           |      0      |    0      |       0      |    1      |     125 |
|          32 | False    | no RDT flag        | ftd_mean                      |     59.2928 |   59.1694 |      -0.1234 |    0.6043 |     125 |
|          32 | False    | no RDT flag        | time_to_block_mean            |    122.186  |  122.506  |       0.3193 |    0.3779 |     125 |
|          32 | False    | no RDT flag        | node_legit_blocked            |      0      |    0      |       0      |    1      |     125 |
|          32 | False    | no RDT flag        | attack_dio_processed_per_node |    322.749  |  322.67   |      -0.0794 |    0.597  |     125 |
|          32 | False    | no validation      | accuracy                      |      1      |    0.9849 |      -0.0151 |    0      |     125 |
|          32 | False    | no validation      | f1                            |      1      |    0.9773 |      -0.0227 |    0      |     125 |
|          32 | False    | no validation      | precision                     |      1      |    0.9595 |      -0.0405 |    0      |     125 |
|          32 | False    | no validation      | recall                        |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | no validation      | fpr                           |      0      |    0.0244 |       0.0244 |    0      |     125 |
|          32 | False    | no validation      | ftd_mean                      |     59.2928 |   59.2928 |       0      |    1      |     125 |
|          32 | False    | no validation      | time_to_block_mean            |    122.186  |   59.2928 |     -62.8935 |    0      |     125 |
|          32 | False    | no validation      | node_legit_blocked            |      0      |    0.76   |       0.76   |    0      |     125 |
|          32 | False    | no validation      | attack_dio_processed_per_node |    322.749  |  188.482  |    -134.268  |    0      |     125 |
|          32 | False    | fixed MD = 3       | accuracy                      |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | fixed MD = 3       | f1                            |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | fixed MD = 3       | precision                     |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | fixed MD = 3       | recall                        |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | fixed MD = 3       | fpr                           |      0      |    0      |       0      |    1      |     125 |
|          32 | False    | fixed MD = 3       | ftd_mean                      |     59.2928 |   59.2928 |       0      |    1      |     125 |
|          32 | False    | fixed MD = 3       | time_to_block_mean            |    122.186  |  119.33   |      -2.8566 |    1      |     125 |
|          32 | False    | fixed MD = 3       | node_legit_blocked            |      0      |    0      |       0      |    1      |     125 |
|          32 | False    | fixed MD = 3       | attack_dio_processed_per_node |    322.749  |  369.945  |      47.1955 |    0.0338 |     125 |
|          32 | False    | STIA within window | accuracy                      |      1      |    0.9949 |      -0.0051 |    0.0002 |     125 |
|          32 | False    | STIA within window | f1                            |      1      |    0.9905 |      -0.0095 |    0.0002 |     125 |
|          32 | False    | STIA within window | precision                     |      1      |    0.9834 |      -0.0166 |    0.0002 |     125 |
|          32 | False    | STIA within window | recall                        |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | STIA within window | fpr                           |      0      |    0.0079 |       0.0079 |    0.0002 |     125 |
|          32 | False    | STIA within window | ftd_mean                      |     59.2928 |   30      |     -29.2928 |    0      |     125 |
|          32 | False    | STIA within window | time_to_block_mean            |    122.186  |   93.0596 |     -29.1267 |    0      |     125 |
|          32 | False    | STIA within window | node_legit_blocked            |      0      |    0.248  |       0.248  |    0.0001 |     125 |
|          32 | False    | STIA within window | attack_dio_processed_per_node |    322.749  |  232.512  |     -90.2372 |    0      |     125 |
|          32 | False    | STIA persistent    | accuracy                      |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | STIA persistent    | f1                            |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | STIA persistent    | precision                     |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | STIA persistent    | recall                        |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | STIA persistent    | fpr                           |      0      |    0      |       0      |    1      |     125 |
|          32 | False    | STIA persistent    | ftd_mean                      |     59.2928 |   85.1472 |      25.8544 |    0      |     125 |
|          32 | False    | STIA persistent    | time_to_block_mean            |    122.186  |  148.948  |      26.762  |    0      |     125 |
|          32 | False    | STIA persistent    | node_legit_blocked            |      0      |    0      |       0      |    1      |     125 |
|          32 | False    | STIA persistent    | attack_dio_processed_per_node |    322.749  |  359.779  |      37.0295 |    0      |     125 |
|          32 | False    | Mamdani COG        | accuracy                      |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | Mamdani COG        | f1                            |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | Mamdani COG        | precision                     |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | Mamdani COG        | recall                        |      1      |    1      |       0      |    1      |     125 |
|          32 | False    | Mamdani COG        | fpr                           |      0      |    0      |       0      |    1      |     125 |
|          32 | False    | Mamdani COG        | ftd_mean                      |     59.2928 |   51.3385 |      -7.9543 |    0      |     125 |
|          32 | False    | Mamdani COG        | time_to_block_mean            |    122.186  |  129.412  |       7.2256 |    0.0001 |     125 |
|          32 | False    | Mamdani COG        | node_legit_blocked            |      0      |    0      |       0      |    1      |     125 |
|          32 | False    | Mamdani COG        | attack_dio_processed_per_node |    322.749  |  323.947  |       1.1981 |    0.5799 |     125 |
|          32 | True     | no STIA            | accuracy                      |      0.9617 |    0.376  |      -0.5857 |    0      |     125 |
|          32 | True     | no STIA            | f1                            |      0.9168 |    0.4705 |      -0.4463 |    0      |     125 |
|          32 | True     | no STIA            | precision                     |      0.8785 |    0.3285 |      -0.55   |    0      |     125 |
|          32 | True     | no STIA            | recall                        |      0.9674 |    0.9999 |       0.0325 |    0      |     125 |
|          32 | True     | no STIA            | fpr                           |      0.0412 |    0.8825 |       0.8413 |    0      |     125 |
|          32 | True     | no STIA            | ftd_mean                      |     37.0828 |   30      |      -7.0828 |    0      |     125 |
|          32 | True     | no STIA            | time_to_block_mean            |    126.498  |  100.541  |     -25.957  |    0      |     125 |
|          32 | True     | no STIA            | node_legit_blocked            |      9.96   |   23.232  |      13.272  |    0      |     125 |
|          32 | True     | no STIA            | attack_dio_processed_per_node |   1220.45   |  708.142  |    -512.309  |    0      |     125 |
|          32 | True     | no RDT flag        | accuracy                      |      0.9617 |    0.95   |      -0.0117 |    0      |     125 |
|          32 | True     | no RDT flag        | f1                            |      0.9168 |    0.894  |      -0.0228 |    0      |     125 |
|          32 | True     | no RDT flag        | precision                     |      0.8785 |    0.8392 |      -0.0393 |    0      |     125 |
|          32 | True     | no RDT flag        | recall                        |      0.9674 |    0.9702 |       0.0028 |    0.0155 |     125 |
|          32 | True     | no RDT flag        | fpr                           |      0.0412 |    0.0588 |       0.0176 |    0      |     125 |
|          32 | True     | no RDT flag        | ftd_mean                      |     37.0828 |   38.0664 |       0.9835 |    0.0865 |     125 |
|          32 | True     | no RDT flag        | time_to_block_mean            |    126.498  |  126.246  |      -0.2524 |    0.6995 |     125 |
|          32 | True     | no RDT flag        | node_legit_blocked            |      9.96   |   12.6    |       2.64   |    0      |     125 |
|          32 | True     | no RDT flag        | attack_dio_processed_per_node |   1220.45   | 1219.86   |      -0.5871 |    0.4084 |     125 |
|          32 | True     | no validation      | accuracy                      |      0.9617 |    0.356  |      -0.6057 |    0      |     125 |
|          32 | True     | no validation      | f1                            |      0.9168 |    0.4606 |      -0.4562 |    0      |     125 |
|          32 | True     | no validation      | precision                     |      0.8785 |    0.3175 |      -0.561  |    0      |     125 |
|          32 | True     | no validation      | recall                        |      0.9674 |    1      |       0.0326 |    0      |     125 |
|          32 | True     | no validation      | fpr                           |      0.0412 |    0.917  |       0.8758 |    0      |     125 |
|          32 | True     | no validation      | ftd_mean                      |     37.0828 |   37.0978 |       0.015  |    0.3173 |     125 |
|          32 | True     | no validation      | time_to_block_mean            |    126.498  |   37.0978 |     -89.4002 |    0      |     125 |
|          32 | True     | no validation      | node_legit_blocked            |      9.96   |   22.424  |      12.464  |    0      |     125 |
|          32 | True     | no validation      | attack_dio_processed_per_node |   1220.45   |  548.044  |    -672.407  |    0      |     125 |
|          32 | True     | fixed MD = 3       | accuracy                      |      0.9617 |    0.9515 |      -0.0102 |    0      |     125 |
|          32 | True     | fixed MD = 3       | f1                            |      0.9168 |    0.8979 |      -0.0189 |    0      |     125 |
|          32 | True     | fixed MD = 3       | precision                     |      0.8785 |    0.8355 |      -0.043  |    0      |     125 |
|          32 | True     | fixed MD = 3       | recall                        |      0.9674 |    0.9884 |       0.021  |    0      |     125 |
|          32 | True     | fixed MD = 3       | fpr                           |      0.0412 |    0.0642 |       0.0231 |    0      |     125 |
|          32 | True     | fixed MD = 3       | ftd_mean                      |     37.0828 |   37.0828 |       0      |    1      |     125 |
|          32 | True     | fixed MD = 3       | time_to_block_mean            |    126.498  |  104.824  |     -21.6744 |    0.0004 |     125 |
|          32 | True     | fixed MD = 3       | node_legit_blocked            |      9.96   |   12.48   |       2.52   |    0      |     125 |
|          32 | True     | fixed MD = 3       | attack_dio_processed_per_node |   1220.45   | 1420.87   |     200.415  |    0.0168 |     125 |
|          32 | True     | STIA within window | accuracy                      |      0.9617 |    0.3843 |      -0.5775 |    0      |     125 |
|          32 | True     | STIA within window | f1                            |      0.9168 |    0.4738 |      -0.443  |    0      |     125 |
|          32 | True     | STIA within window | precision                     |      0.8785 |    0.3317 |      -0.5468 |    0      |     125 |
|          32 | True     | STIA within window | recall                        |      0.9674 |    0.9999 |       0.0325 |    0      |     125 |
|          32 | True     | STIA within window | fpr                           |      0.0412 |    0.8704 |       0.8292 |    0      |     125 |
|          32 | True     | STIA within window | ftd_mean                      |     37.0828 |   30      |      -7.0828 |    0      |     125 |
|          32 | True     | STIA within window | time_to_block_mean            |    126.498  |  100.871  |     -25.6265 |    0      |     125 |
|          32 | True     | STIA within window | node_legit_blocked            |      9.96   |   23.208  |      13.248  |    0      |     125 |
|          32 | True     | STIA within window | attack_dio_processed_per_node |   1220.45   |  712.713  |    -507.739  |    0      |     125 |
|          32 | True     | STIA persistent    | accuracy                      |      0.9617 |    0.9717 |       0.01   |    0      |     125 |
|          32 | True     | STIA persistent    | f1                            |      0.9168 |    0.9429 |       0.0261 |    0      |     125 |
|          32 | True     | STIA persistent    | precision                     |      0.8785 |    0.9793 |       0.1008 |    0      |     125 |
|          32 | True     | STIA persistent    | recall                        |      0.9674 |    0.9174 |      -0.0499 |    0      |     125 |
|          32 | True     | STIA persistent    | fpr                           |      0.0412 |    0.0051 |      -0.0361 |    0      |     125 |
|          32 | True     | STIA persistent    | ftd_mean                      |     37.0828 |   91.3955 |      54.3127 |    0      |     125 |
|          32 | True     | STIA persistent    | time_to_block_mean            |    126.498  |  211.071  |      84.5731 |    0      |     125 |
|          32 | True     | STIA persistent    | node_legit_blocked            |      9.96   |    2.096  |      -7.864  |    0      |     125 |
|          32 | True     | STIA persistent    | attack_dio_processed_per_node |   1220.45   | 1161.31   |     -59.1381 |    0.3824 |     125 |
|          32 | True     | Mamdani COG        | accuracy                      |      0.9617 |    0.9236 |      -0.0381 |    0      |     125 |
|          32 | True     | Mamdani COG        | f1                            |      0.9168 |    0.8494 |      -0.0674 |    0      |     125 |
|          32 | True     | Mamdani COG        | precision                     |      0.8785 |    0.767  |      -0.1115 |    0      |     125 |
|          32 | True     | Mamdani COG        | recall                        |      0.9674 |    0.9831 |       0.0158 |    0      |     125 |
|          32 | True     | Mamdani COG        | fpr                           |      0.0412 |    0.1005 |       0.0593 |    0      |     125 |
|          32 | True     | Mamdani COG        | ftd_mean                      |     37.0828 |   35.1055 |      -1.9774 |    0      |     125 |
|          32 | True     | Mamdani COG        | time_to_block_mean            |    126.498  |  145.195  |      18.6972 |    0      |     125 |
|          32 | True     | Mamdani COG        | node_legit_blocked            |      9.96   |   15.976  |       6.016  |    0      |     125 |
|          32 | True     | Mamdani COG        | attack_dio_processed_per_node |   1220.45   | 1135.78   |     -84.6691 |    0      |     125 |

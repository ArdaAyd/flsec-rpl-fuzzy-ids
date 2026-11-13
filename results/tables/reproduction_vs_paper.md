|   sensors | network   | method                   | accuracy (ours)   | accuracy (paper)   | f1 (ours)   | f1 (paper)   | ftd_s (ours)   | ftd_s (paper)   |
|----------:|:----------|:-------------------------|:------------------|:-------------------|:------------|:-------------|:---------------|:----------------|
|        16 | static    | Anomaly-Based IDS        | 59-73             | 49-64              | 35-67       | 21-51        | 30-325         | 27-698          |
|        16 | static    | CoSec-RPL                | 54-88             | 49-66              | 0-0         | 1-27         | no detection   | 27-612          |
|        16 | static    | CoSec-RPL (sigma = 10 s) | 54-90             |                    | 0-21        |              | 30-30          |                 |
|        16 | static    | FLSec-RPL                | 97-100            | 97-100             | 95-100      | 91-100       | 48-62          | 27-45           |
|        16 | mobile    | Anomaly-Based IDS        | 24-62             | 58-94              | 24-73       | 9-83         | 30-38          | 28-631          |
|        16 | mobile    | CoSec-RPL                | 50-88             | 61-98              | 0-0         | 14-97        | no detection   | 28-348          |
|        16 | mobile    | CoSec-RPL (sigma = 10 s) | 54-95             |                    | 17-88       |              | 30-333         |                 |
|        16 | mobile    | FLSec-RPL                | 83-99             | 75-100             | 62-99       | 60-100       | 30-54          | 31-110          |
|        32 | static    | Anomaly-Based IDS        | 33-69             | 61-72              | 21-75       | 13-31        | 30-104         | 27-564          |
|        32 | static    | CoSec-RPL                | 50-91             | 66-95              | 0-0         | 14-70        | no detection   | 27-470          |
|        32 | static    | CoSec-RPL (sigma = 10 s) | 51-98             |                    | 1-89        |              | 30-712         |                 |
|        32 | static    | FLSec-RPL                | 100-100           | 96-99              | 100-100     | 93-99        | 55-61          | 27-69           |
|        32 | mobile    | Anomaly-Based IDS        | 15-56             | 66-95              | 18-70       | 16-86        | 30-31          | 33-710          |
|        32 | mobile    | CoSec-RPL                | 50-91             | 65-98              | 0-0         | 10-94        | no detection   | 28-690          |
|        32 | mobile    | CoSec-RPL (sigma = 10 s) | 53-95             |                    | 10-93       |              | 30-124         |                 |
|        32 | mobile    | FLSec-RPL                | 90-100            | 70-99              | 74-100      | 25-99        | 30-46          | 53-490          |

# Portuguese Fund Quotes Scrapper

Scrap quotes from various funds and banks existing in Portugal.

## Feature Support
- MySQL database for storing quotes.

## Useful developer resources

- [ArgParse](https://docs.python.org/3/library/argparse.html)
- [ConfigArgParse](https://github.com/bw2/ConfigArgParse)
- [Peewee ORM](http://docs.peewee-orm.com/en/latest/)
- [Peewee ORM: Multi-Threaded Applications](http://docs.peewee-orm.com/en/latest/peewee/database.html#multi-threaded-applications)
- [Querying the top N objects per group with Peewee ORM](https://charlesleifer.com/blog/querying-the-top-n-objects-per-group-with-peewee-orm/)
- [MySQL JOIN the most recent row only?](https://stackoverflow.com/a/35965649/1546848)
- [Python Requests](https://requests.readthedocs.io/en/master/)
- [urllib3](https://urllib3.readthedocs.io/en/latest/)
- [urllib3 - set max retries](https://stackoverflow.com/questions/15431044/can-i-set-max-retries-for-requests-request)
- [BeautifulSoup](https://beautiful-soup-4.readthedocs.io/en/latest/)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [Jinja2](https://jinja2docs.readthedocs.io/en/stable/)


## Disclaimer

This software allows scrapping of public information.
We're not responsible for this information and we're not responsible for what users do with it.

## Requirements
- Python 3.7+
- MySQL 5.7+

### Libraries
- configargparse==1.5.3
- flask==2.3.2
- pymysql==1.0.3
- peewee==3.16.2
- pysocks==1.7.1
- requests==2.31
- beautifulsoup4==4.12.2
- pycountry==22.3.5

## TODO
- Add AlvesRibeiro PPR from BankInvest

## Usage

```
usage: app.py [-h] [-cf CONFIG] [-v] [--log-path LOG_PATH] [--download-path DOWNLOAD_PATH] [-ua {random,chrome,firefox,safari}] --db-name DB_NAME --db-user DB_USER --db-pass DB_PASS [--db-host DB_HOST] [--db-port DB_PORT]
              [--db-max-conn DB_MAX_CONN] [--db-batch-size DB_BATCH_SIZE] [-Sf SCRAPPER_FREQUENCY] [-Sr SCRAPPER_RETRIES] [-Sbf SCRAPPER_BACKOFF_FACTOR] [-St SCRAPPER_TIMEOUT] [-Sp SCRAPPER_PROXY]

optional arguments:
  -h, --help            show this help message and exit
  -cf CONFIG, --config CONFIG
                        Set configuration file.
  -v, --verbose         Control verbosity level, e.g. -v or -vv.
  --log-path LOG_PATH   Directory where log files are saved.
  --download-path DOWNLOAD_PATH
                        Directory where downloaded files are saved.
  -ua {random,chrome,firefox,safari}, --user-agent {random,chrome,firefox,safari}
                        Browser User-Agent used. Default: random

Database:
  --db-name DB_NAME     Name of the database to be used. [env var: MYSQL_DATABASE]
  --db-user DB_USER     Username for the database. [env var: MYSQL_USER]
  --db-pass DB_PASS     Password for the database. [env var: MYSQL_PASSWORD]
  --db-host DB_HOST     IP or hostname for the database. [env var: MYSQL_HOST]
  --db-port DB_PORT     Port for the database. [env var: MYSQL_PORT]
  --db-max-conn DB_MAX_CONN
                        Maximum number of connections to the database. [env var: MYSQL_MAX_CONN]
  --db-batch-size DB_BATCH_SIZE
                        Maximum number of rows to update per batch. [env var: MYSQL_BATCH_SIZE]

Scrapper:
  -Sf SCRAPPER_FREQUENCY, --scrapper-frequency SCRAPPER_FREQUENCY
                        Scrap quotes very X hours. Default: 6.
  -Sr SCRAPPER_RETRIES, --scrapper-retries SCRAPPER_RETRIES
                        Maximum number of web request attempts. Default: 5.
  -Sbf SCRAPPER_BACKOFF_FACTOR, --scrapper-backoff-factor SCRAPPER_BACKOFF_FACTOR
                        Time factor (in seconds) by which the delay until next retry will increase. Default: 1.0.
  -St SCRAPPER_TIMEOUT, --scrapper-timeout SCRAPPER_TIMEOUT
                        Connection timeout in seconds. Default: 5.
  -Sp SCRAPPER_PROXY, --scrapper-proxy SCRAPPER_PROXY
                        Use this proxy for webpage scrapping. Format: <proto>://[<user>:<pass>@]<ip>:<port> Default: None.

Args that start with '--' (eg. -v) can also be set in a config file (app\config\config.ini or specified via -cf). Config file syntax allows: key=value, flag=true, stuff=[a,b,c] (for details, see syntax at https://goo.gl/R74nmi).
If an arg is specified in more than one place, then commandline values override environment variables which override config file values which override defaults.
```


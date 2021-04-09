# Synchronization of RSEs, Protocols, Distances from ESCAPE-CRIC
For a more detailed description please take a look [here](https://wiki.escape2020.de/index.php/WP2_-_DIOS#3.7_Information_and_Configuration_System).

## How-to

The Rucio Server should be installed and the DB should be configured.

You can install the rucio server via pip:
```bash
pip install rucio
```

You should configure the following section in your ```rucio.cfg``` file:
```
[database]
default = $DB_URL
pool_reset_on_return = rollback
echo = 0
pool_recycle = 600
```

Finally you should be able to run the script:
```bash
python sync_cric_rucio.py
```

Please note that the CRIC urls are hardcoded, you should change that in case you need to synchronize from a different service.

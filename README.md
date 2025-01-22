# f2pool-monitor
F2Pool API script to monitor hashrate with Zabbix 5

# How it works

* Get metrics from F2pool thrue API
* Parse data from JSON output
* Store data into Zabbix

# Install
* Download f2pool_monitor.py and f2pool_template.xml
* Put f2pool_monitor.py into ExternalScript location (usual /usr/lib/zabbix/externalscripts)
* Edit "api_secret": "YOUR_API_SECRET" section wit your API key in f2pool_monitor.py
* Make f2pool_monitor.py executable (`chmod 755 f2pool_monitor.py`)
* Import f2pool_template.xml into zabbix
* Add Pool as Zabbix Host with ip 127.0.0.1 , use Zabbix Agent type
* Add Zabbix Macros `{$F2POOL.USERNAME}` with your username you want to monitor
* Add Zabbix Macros `{$HASHRATE.MIN.WARN}` if you want the triger works
* Link template to Your host

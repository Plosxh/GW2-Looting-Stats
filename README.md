# 💰 GW2 - Looting Stats

So I was playing some [Guild Wars 2](https://www.guildwars2.com/) these days, just collecting stuff I needed to get the [skyscale mount](https://wiki.guildwars2.com/wiki/Skyscale), when I noticed that it's kinda difficult for me to keep track of which items I already have enough of and which ones I still have to farm further.

Thats why I created this little helper script. Thats why I created this little helper script. It's able to read a pre-configured looting-target config (like the sample `skyscale_mount.json`) and can then provide an overview of the current materials/inventory stats for that specific looting-target by utilizing the [GW2 API](https://wiki.guildwars2.com/wiki/API:Main) to do that.

## 🖥️ Sample Output

## 🛠️ Getting started

### Preparations:
Go to https://account.arena.net/applications and generate a new API Key with at least the scopes:
	 `wallet`, `account`, `inventories`, `characters`
	 
Create a `.env` file from the given sample `.env.dist` and add the created API Key:
```
  GW2_API_KEY=[YOUR_API_KEY_HERE]
  CONFIG_FILE=skyscale_mount.json
  GROUPED=true
  REFRESH=300
  LANG=en
```
Here you can also change any other configuration as you like. More to that at ...

### Setup venv:
```
  $ python -m venv ./venv
  $ .\venv\Scripts\activate
```

### Install requirements and run:
```
  $ pip install -r requirements.txt
  $ python main.py
```

## ⚙️ Configuration

|ENV-Variable|Description|
|--|--|
| GW2_API_KEY | The secret GW2 API key to use.  |
| CONFIG_FILE | The pre-configured looting-target config filepath. |
| GROUPED | `true` or `false` ➜ Toggle if currency and material items should be grouped in seperated tables or displayed in a single table. |
| REFRESH | Auto-Refresh countdown in seconds. Set to `0` to disable it. |
| LANG | Language code for the GW2 API. Valid languages are `en`, `es`, `de`, `fr` and `zh`. |


## 📋 References
 - https://pypi.org/project/GuildWars2-API-Client/
 - https://wiki.guildwars2.com/wiki/API:Main
	 - https://wiki.guildwars2.com/wiki/API:2/items
	 - https://wiki.guildwars2.com/wiki/API:2/account/bank
	 - https://wiki.guildwars2.com/wiki/API:2/account/wallet
	 - https://wiki.guildwars2.com/wiki/API:2/account/materials
	 - https://wiki.guildwars2.com/wiki/API:2/account/inventory
	 - https://wiki.guildwars2.com/wiki/API:2/characters
	 - https://wiki.guildwars2.com/wiki/API:2/characters/:id/inventory

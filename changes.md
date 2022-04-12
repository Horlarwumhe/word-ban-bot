
Added `config.py` file for storing bot configurations instead of using environmental variable

Add new configuration for the bot
```py

ALLOWED_UPDATES = []
```
Use the variable

```py

from bot import config

allow_updates = config.ALLOWED_UPDATES

```

Note:

Bot token should be put in environmet

```py

BOT_TOKEN = os.environ.get("BOT_TOKEN")

```
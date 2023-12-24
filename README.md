# psindia-bot

Dependencies can be installed via the `requirements.txt` file

```py
$ python3 -m venv ps_venv # Create a virtualenv
$ . ./ps_venv/bin/activate

$ pip install -r requirements.txt
```

# Config

```json
{
  "token": "my-secret-token",
  "ps_token": "my-secret-ps-token",
  "public_key": "my-secret-key",
  "application_id": "my-application-id",
  "authorization_url": "https://localhost:443",
  "port": 8000,
  "guilds": [],
  "refresh_interval_hours": 12,
  "roles_threshold": {
    "Plathunter - I": 1,
    "Plathunter - II": 10,
    "Plathunter - III": 50
  }
}
```

1. `token`: Discord bot token
2. `ps_token`: PSN token, follow the instructions at https://github.com/isFakeAccount/psnawp for obtaining one
3. `public_key`: From the Discord Application
4. `application_id`: From the Discord Application
5. `authorization_url`: OAuth2 authentication URL, should be in the format `https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&redirect_uri=REDIRECT_URI&response_type=token&scope=identify%20connections` where `CLIENT_ID` is replaced with the `application_id` (eg. `1089479051129453613`) and the `REDIRECT_URI` is replaced with the urlencoded URL of the hosted [frontend](https://github.com/playstation-india/playstation-india.github.io), eg `https%3A%2F%2Fplaystation-india.github.io`
6. `port`: The port the backend will listen at
7. `guilds`: An array of guild IDs where the bot will respond to messages
8. `refresh_interval_hours`: Interval (in hours) after which PSN trophies are scraped
9. `roles_threshold`: The number of platinum trophies the user should have before the given role is granted. Eg. `Plathunter - III` requires atleast `50` trophies

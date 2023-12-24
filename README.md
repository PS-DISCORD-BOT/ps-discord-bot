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

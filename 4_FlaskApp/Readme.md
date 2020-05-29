**Replace the following place holder in utils/config.py**

```python
cloud_config={cloud_config}
email_config= {SEND_GRID_KEY}
invite_url= {Slack invite url}
```

**To start the server**

```bash
python app.py
```



app.py: Server side code

utils/firefu.py: Consists of helper functions for interacting with firebase DB and sending slack invite emails

utils/config.py: Consists of placeholders for cloud api keys, slack invite url and send_grid_api key
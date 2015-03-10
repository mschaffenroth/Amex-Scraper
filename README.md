# Amex-Scraper

## This Can be Used to Scrape Transaction History from American Express!
## To use this module, simply:
### This Will Login Automatically
```python
am = Amex(USERNAME, PASSWORD)
```

### You Can also use 
```python
am = Amex()
am.login(USERNAME, PASSWORD)
```

### Auto Load 30 days of history from account
```python
df = am.load_history()
```

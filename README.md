# Amex-Scraper

## This Can be Used to Scrape Transaction History from American Express!

### This Will Login Automatically
```python
am = Amex(USERNAME, PASSWORD)
```

### You Can also use 
```python
am = Amex()
am.login(USERNAME, PASSWORD)
```

### Auto Load past 10 months of history from account
```python
df = am.load_history()
```

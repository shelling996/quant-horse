import os, pandas as pd
print("scrape_hkjc.py: skip real scrape, use existing races.csv")
# 保留框架，日後可擴展真爬蟲
if not os.path.exists('races.csv'):
    print("No races.csv, main.py will generate emergency one")

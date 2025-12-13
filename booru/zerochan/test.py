from zerochan_scraper import ZerochanScraper

zs = ZerochanScraper()

response = zs._make_request("https://static.zerochan.net/Honma.Meiko.full.2864201.jpg")
print(response)
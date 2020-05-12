import requests

def trigger_webhook(url):
	requests.post(url)
	
def trigger_webhooks(urls):
	for url in urls:
		trigger_webhook(url)
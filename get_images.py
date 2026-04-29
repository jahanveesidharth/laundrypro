import urllib.request, re, json, urllib.parse

items = ["Shirt", "T-Shirt", "Pants", "Jeans", "Saree", "Suit", "Jacket", "Kurta", "Dress", "Blanket", "Bedsheet", "Curtain", "Sweater", "Blazer", "Lehenga", "Dupatta", "Salwar Kameez", "Coat", "Tie", "Laundry basket"]

out = {}
for q in items:
    req = urllib.request.Request('https://unsplash.com/napi/search/photos?query=' + urllib.parse.quote(q) + '&per_page=3', headers={'User-Agent': 'Mozilla/5.0'})
    try:
        data = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
        if data and 'results' in data and len(data['results']) > 0:
            out[q] = data['results'][0]['urls']['raw'] + "&w=400&q=80"
        else:
            out[q] = ""
    except Exception as e:
        print(f"Error for {q}: {e}")
        out[q] = ""
print(json.dumps(out, indent=2))

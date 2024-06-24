import random
from flask import Flask, render_template, request, redirect
from bs4 import BeautifulSoup
from tinydb import TinyDB, Query
import requests
import time

app = Flask(__name__)
db = TinyDB('tracked_products.json')
Product = Query()

def get_user_agent():
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0'
    ]
    return random.choice(user_agent_list)

def scrape_product_data(url, target_price):
    while True:
        browser_header = {
            "User-Agent": get_user_agent()
        }

        try:
            response = requests.get(url, headers=browser_header)
            response.raise_for_status() 
            soup = BeautifulSoup(response.content, 'html.parser')

            product_title = soup.select_one("#productTitle")
            product_image_element = soup.select_one("#imgTagWrapperId img")
            product_price_element = soup.select_one(".a-price .a-offscreen")

            if product_title and product_image_element and product_price_element:
                product_name = product_title.get_text(strip=True)
                product_image_url = product_image_element.get("src")
                product_price = product_price_element.get_text(strip=True)
                product_price = float(product_price.replace('R$', '').replace('.', '').replace(',', '.'))

                if product_price <= float(target_price):
                    price_comparison = "lower"
                else:
                    price_comparison = "higher"

                product_data = {
                    "name": product_name,
                    "image_url": product_image_url,
                    "price": product_price,
                    "price_comparison": price_comparison
                }

                return product_data
            else:
                time.sleep(5)  

        except requests.RequestException as e:
            print("Error:", e)
            time.sleep(5)

        except Exception as ex:
            print("An unexpected error occurred:", ex)
            time.sleep(5)

@app.route("/")
def home():
    products = db.all()
    return render_template('index.html', products=products)

@app.route('/add_product', methods=['POST'])
def add_product():
    product_url = request.form['product_url']
    target_price = request.form['target_price']
    product_data = scrape_product_data(product_url, target_price)
    if product_data:
        db.insert({'name': product_data['name'], 'image_url': product_data['image_url'], 'price': product_data['price'], 'target_price': target_price, 'url': product_url, 'price_comparison': product_data['price_comparison']})
    return redirect('/')

@app.route('/delete_product', methods=['POST'])
def delete_product():
    product_id = int(request.form['product_id'])
    db.remove(doc_ids=[product_id])
    return redirect('/')

@app.route('/update_prices', methods=['POST'])
def update_prices():
    for product in db.all():
        product_data = scrape_product_data(product["url"], product["target_price"])
        if product_data:
            product_price = product_data["price"]
            price_comparison  = product_data["price_comparison"]
            db.update({"price": product_price, "price_comparison": price_comparison}, Product.url == product["url"])
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)

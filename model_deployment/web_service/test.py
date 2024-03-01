import requests
import predict

url = "http://localhost:9696/predict"

stock = {
    "Symbol" : "SPY"
}

response = requests.post(url, json=stock)
print(response.json())

# pred = predict.predict(stock)
# print(round(pred, 4))
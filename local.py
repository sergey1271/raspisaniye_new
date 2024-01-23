import requests
res = requests.post("http://127.0.0.1:5000/get_info", files={'upload_file': open('New Text Document.txt', 'r')})
print("status code:", res.status_code)
# print("JSON:", res.json())
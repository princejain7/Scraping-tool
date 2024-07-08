**Create a virtual env**

python -m venv env

source env/bin/activate


**Install the dependencies**

pip install -r requirements.txt

**Ensure Redis is installed and running**

sudo apt-get install redis-server

sudo service redis-server start

**Start the FastAPI server**

uvicorn app.main:app --reload

**Make a POST request to start scraping**

curl -X 'POST' \
  'http://127.0.0.1:8000/scrape' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your-auth-token' \
  -d '{
  "page_limit": 2
}'

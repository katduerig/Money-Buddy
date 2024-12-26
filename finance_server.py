import processing
import sheets
from urllib.parse import unquote
from datetime import datetime

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, JSONResponse, HTMLResponse, FileResponse
from starlette.routing import Route
import uvicorn
import json

# this file gives the browser the website and collects input from user
async def expense_submitted(request):
    data = await request.body()
    data=data.decode("utf-8")
    data=data.replace('+', ' ')
    parameters = data.split('&')
    named_param = {}

    x=0
    while x < len(parameters):
        print(parameters[x])
        full=parameters[x].split('=')
        key = full[0]
        value = full[1]
        named_param[key] = value
        x+=1

    note = ''
    amount = ''
    where = ''
    when = ''
    method = ''
    category = ''
    
    if "note" in named_param and named_param["note"] !="":
        note = unquote(named_param["note"])


    if "amount" in named_param and named_param["amount"] !="":
        amount_signless= named_param["amount"]
        amount_signless=unquote(amount_signless)
        if "$" not in amount_signless:
            amount_signless="$"+amount_signless
        if "-" not in amount_signless:
            amount_signless="-"+amount_signless
        amount=amount_signless

    if "where" in named_param and named_param["where"] !="":
        where = named_param["where"]
    
    if "when" in named_param and named_param["when"] !="":
        when = named_param["when"]
        date_object = datetime.strptime(when, "%Y-%m-%d")
        formatted_date = date_object.strftime("%m/%d/%y").lstrip('0').replace('/0', '/')
        when=formatted_date

    if "method" in named_param and named_param["method"] !="":
        method = named_param["method"]

    if "category" in named_param and named_param["category"] !="":
        category = named_param["category"]

    sheets.insert_one_row(when,amount,category,note,where,method)

    with open('frontend/thanks.html') as f:
        return HTMLResponse(f.read())


async def get_month_totals(request):
    month_totals= processing.get_all_totals(processing.total_data)
    string_version= json.dumps(month_totals)
    return PlainTextResponse(string_version)

async def get_monthly_category_totals(request):
    month_totals= processing.get_monthly_category_totals()
    string_version= json.dumps(month_totals)
    return PlainTextResponse(string_version)

#from chatgpt for submitting income
async def income_submitted(request):
    data = await request.body()
    data = data.decode("utf-8")
    data = data.replace('+', ' ')
    parameters = data.split('&')
    named_param = {}

    for param in parameters:
        key, value = param.split('=')
        named_param[key] = value

    # Retrieve each form field
    source = unquote(named_param.get("source", ""))
    amount = unquote(named_param.get("amount", ""))
    date = unquote(named_param.get("date", ""))
    date_object = datetime.strptime(date, "%Y-%m-%d")
    date = date_object.strftime("%m/%d/%y").lstrip('0').replace('/0', '/')
    note = unquote(named_param.get("note", ""))

    # Send data to the income sheet
    sheets.insert_income_row(date, amount, source, note)

    # Send the user to a thank-you page
    with open('frontend/thanks.html') as f:
        return HTMLResponse(f.read())


import pathlib
def file_delivery(filename):
    if type(filename) is str:
        filepath = pathlib.Path('frontend', filename)
    else:
        filepath = filename
    def inner(request):
        if filepath.name.endswith('.html'):
            with open(filepath) as f:
                return HTMLResponse(f.read())
        return FileResponse(filepath)
    return inner


class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response


routes = [
    # Data URLS
    Route('/get_month_totals', endpoint=get_month_totals),
    Route('/get_monthly_category_totals', endpoint=get_monthly_category_totals),
    
    Route('/info', endpoint=expense_submitted, methods=['POST']),
    Route('/submit_income', endpoint=income_submitted, methods=['POST']),

    # File delivery
    Route('/', endpoint=file_delivery('index.html')),
    Route('/purchases.html', endpoint=file_delivery('purchases.html')),
    Route('/thanks.html', endpoint=file_delivery('thanks.html')),
    Route('/index.html', endpoint=file_delivery('index.html')),
    Route('/income.html', endpoint=file_delivery('income.html')),
    Route('/calculations.html', endpoint=file_delivery('calculations.html')),
    Route('/income_totals.html', endpoint=file_delivery('income_totals.html')),

    Route('/homepage.css', endpoint=file_delivery('homepage.css')),
    Route('/purchases.css', endpoint=file_delivery('purchases.css')),
    Route('/thanks.css', endpoint=file_delivery('thanks.css')),
    Route('/income.css', endpoint=file_delivery('income.css')),
    Route('/calculations.css', endpoint=file_delivery('calculations.css')),

    Route('/master.css', endpoint=file_delivery('master.css')),
]

image_dir = pathlib.Path('frontend', 'images')
for filepath in image_dir.glob('**/*'):
    just_name = '/' + filepath.name
    routes.append(Route(just_name, endpoint=file_delivery(filepath)))

app = Starlette(routes=routes)
app.add_middleware(NoCacheMiddleware)

PORT = 8000
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 80))
local_ip = s.getsockname()[0]
s.close()
print(f'Go to http://{local_ip}:{PORT}')
uvicorn.run(app, host='0.0.0.0', port=PORT)

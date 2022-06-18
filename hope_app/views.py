import os
import urllib.request
from xml.dom import minidom

import apiclient
import httplib2
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView
from oauth2client.service_account import ServiceAccountCredentials

from hope_app.models import Order


class IndexView(TemplateView):
    template_name = "hope_app/main.html"        # main.html created


def api_connect():
    current_direction = os.path.dirname(os.path.abspath(__file__))
    cred_json = '{}\\static\\cred.json'.format(current_direction)
    spreadsheet_id = '1gfou6Uw32IEcMM3ZeMVbOUUwn79BjDxlsC7DDcB3tqQ'

    credentials = ServiceAccountCredentials.from_json_keyfile_name(         # connected to Google API(Sheets, Drive)
        cred_json,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    httpauth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=httpauth)      # services from Sheets v.4

    values = service.spreadsheets().values().get(       # got data from table
        spreadsheetId=spreadsheet_id,
        range='A1:D100',
        majorDimension='ROWS'
    ).execute()

    return values.get('values')


def get_currency():
    url = urllib.request.urlopen('https://www.cbr.ru/scripts/XML_daily.asp')        # XML file from CBR
    dom = minidom.parseString(url.read())       # parsing XML document and normalizing view of doc
    dom.normalize()

    elements = dom.getElementsByTagName("Valute")

    for node in elements:
        for child in node.childNodes:
            if child.nodeType == 1:
                if child.tagName == 'Value':
                    if child.firstChild.nodeType == 3:
                        value = float(child.firstChild.data.replace(',', '.'))
                if child.tagName == 'CharCode':
                    if child.firstChild.nodeType == 3:
                        char_code = child.firstChild.data
        if char_code == 'USD':
            return value


def get_data(request):

    sheet_value = api_connect()     # get data from sheet doc
    USD = get_currency()        # new variable

    for values in sheet_value:
        i = 0

        for value in values:
            if value == '№':
                break
            if i == 0:
                num = value
                i += 1
            elif i == 1:
                order_num = value
                i += 1
            elif i == 2:
                price_USD = float(value)
                i += 1
            elif i == 3:
                date = value
                price_RUB = price_USD * USD
                price_RUB = float('{:.2f}'.format(price_RUB))
                i += 1
            if i == 4:

                try:
                    order = Order.objects.get(id=id)
                    order.order_num = order_num
                    order.price_USD = price_USD
                    order.delivery_date = date
                    order.price_RUB = price_RUB
                except:
                    order = Order(id=num,               # uploading data
                                  order_num=order_num,
                                  price_USD=price_USD,
                                  delivery_date=date,
                                  price_RUB=price_RUB)

                order.save()        # saved in database


    orders = Order.objects.order_by('id')

    if len(orders) > len(sheet_value) - 1:              # delete data

        for i in range(len(sheet_value), len(orders) + 1):
            order = Order.objects.get(id=i)
            order.delete()


    return JsonResponse({"response": list(orders.values())})    # response like json file
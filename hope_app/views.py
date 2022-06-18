import os
import urllib
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
    # Main page
    template_name = "hope_app/main.html"


def api_connect():
    # Get data from credential.json
    # Path .\static\credential.json
    current_direction = os.path.dirname(os.path.abspath(__file__))
    credential_json = '{}\\static\\cred.json'.format(current_direction)
    # Google sheets id
    spreadsheet_id = '1gfou6Uw32IEcMM3ZeMVbOUUwn79BjDxlsC7DDcB3tqQ'

    # We log in and get a service instance of API access
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        credential_json,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    httpauth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=httpauth)

    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='A1:D100',
        majorDimension='ROWS'
    ).execute()

    return values.get('values')


def get_currency():
    # Link for cbr.ru to get all current currencies
    web = urllib.request.urlopen('https://www.cbr.ru/scripts/XML_daily.asp')

    # Parsing cbr.ru
    dom = minidom.parseString(web.read())
    dom.normalize()

    # Looking for Valute tag
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

    # Getting values from Google Sheets
    sheet_value = api_connect()

    # Getting current USDs currency
    usd = get_currency()

    # Saving data in database
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
                price_usd = float(value)
                i += 1
            elif i == 3:
                date = value
                price_rub = price_usd * usd
                price_rub = float('{:.2f}'.format(price_rub))
                i += 1
            if i == 4:
                try:
                    # Updating data by id
                    order = Order.objects.get(id=id)
                    order.order_num = order_num
                    order.price_USD = price_usd
                    order.delivery_date = date
                    order.price_RUB = price_rub
                except:
                    # Creating new data
                    order = Order(id=num,
                                  order_num=order_num,
                                  price_USD=price_usd,
                                  delivery_date=date,
                                  price_RUB=price_rub)
                # Saving in database
                order.save()

    # Getting data from database, order by id
    result = Order.objects.order_by('id')
    # Deleting data from database
    if len(result) > len(sheet_value) - 1:
        for i in range(len(sheet_value), len(result) + 1):
            order = Order.objects.get(id=i)
            order.delete()
    # Returning in Json format
    return JsonResponse({"result": list(result.values())})
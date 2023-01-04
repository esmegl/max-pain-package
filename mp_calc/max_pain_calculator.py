import asks
import json
import trio
from time import time
import requests

from .queries import get_until, get_all, get_most_recent
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta, timezone
from cryptofeed.symbols import Symbol
from cryptofeed.defines import CALL, PUT, OPTION
from .db import (
	ES_HOST,
	max_pain_mapping,
	es_prefix
)

# Find the difference between stock price and strike price
# Multiply the result by open interest at that strike
# Add together the dollar value for the put and call at that strike
# (strike_price - stock_price)*(open_interest) + max(0, X - PA) + max(0, PA - X)
# Being X the strike price and PA actual price of underlaying asset (BTC)
# Repeat for each strike price
# Find the highest value strike price. This price is equivalent to max pain price.

async def main():

	start = datetime.now()

	db_send_channel, db_recv_channel = trio.open_memory_channel(0)

	# Read from database, given an index and a query
	async def read_db(index: str, query: dict) -> list:

		results = []
		response = await asks.get(f'{ES_HOST}/{index}/_search', json=query)
		json_resp = response.json()

		if not "error" in json_resp:
			for hit in json_resp['hits']['hits']:
				results.append(hit)
		else:
			print('No results found')
			print(response.json())

		return results

	# This function changes the instrument name from deribit
	# to cryptofeed Symbol
	def piker_sym_to_cb_sym(name: str) -> Symbol:
		base, expiry_date, strike_price, option_type = tuple(
			name.upper().split('-'))
		quote = base

		if option_type == 'P':
			option_type = PUT
		elif option_type  == 'C':
			option_type = CALL
		else:
			raise Exception("Couldn\'t parse option type")

		return Symbol(
			base,
			quote,
			type=OPTION,
			strike_price=strike_price,
			option_type=option_type,
			expiry_date=expiry_date.upper()
		)

	# Get latest instruments
	def get_instruments_by_date(currency, kind) -> dict:
		payload = {'currency': currency, 'kind': kind}
		r = requests.get('https://test.deribit.com/api/v2/public/get_instruments', params=payload)
		resp = json.loads(r.text)
		response_list = {}

		for i in range(len(resp['result']) // 2):
			element = resp['result'][i]
			instrument_name = str(piker_sym_to_cb_sym(element['instrument_name'])).split('-')
			strike_price, date = int(instrument_name[1]), instrument_name[2].lower()
			if not date in response_list:
				response_list[date] = []

			if not strike_price in response_list[date]:
				response_list[date].append(strike_price)

		return response_list

	# Get open interest for a given strike price
	async def get_open_interest(strike_price: int, date: str, direction: str) -> float:
		open_interest = 0
		index = f'btc-{strike_price}-{date}-{direction}-syncoi'
		results = await read_db(index, get_most_recent())

		if len(results) > 0 and not ('error' in results):
			open_interest += results[0]['_source']['open_interest']
		return open_interest

	# Write to database
	async def database_writer():
		async for index, document in db_recv_channel:
			resp = await asks.post(f'{ES_HOST}/{index}/_doc',
				json=document)
			print('Saved to database')


	async def calculate_max_pain(get_open_interest, instruments: dict) -> float:
		for date in instruments:
			aux = {}
			for strike_price in instruments[date]:
				intrinsic_value = 0
				for sp in instruments[date]:
					intrinsic_value += (max(0, strike_price - sp) * await get_open_interest(sp, date, 'call')) + (max(0, sp - strike_price) * await get_open_interest(sp, date, 'put'))

				if intrinsic_value != 0:
					# Save the strike price and the dollar value for that strike price
					aux[intrinsic_value] = strike_price

			# Store the element with less dollar value for that strike price and date
			if aux != {}:
				date_s = int(time() * 1000)
				current_time = (datetime.utcfromtimestamp(date_s/1000)).isoformat()
				index = es_prefix(f'{date}-{aux[min(aux)]}', 'max-pain')
				document = {
					'max_pain': aux[min(aux)],
					'dollar_value': min(aux),
					'timestamp': current_time
				}
				await db_send_channel.send((index, document))

			print(f'max_pain: {aux[min(aux)]}, dollar_value: {min(aux)}, timestamp: {current_time}')

		print('Execution time: ', datetime.now() - start)

	instruments = get_instruments_by_date('BTC', 'option')

	async with trio.open_nursery() as n:
		n.start_soon(calculate_max_pain, get_open_interest, instruments)
		n.start_soon(database_writer)



es = Elasticsearch(ES_HOST)

es.indices.put_template(
	name='max_pain',
	body=max_pain_mapping)

trio.run(main)

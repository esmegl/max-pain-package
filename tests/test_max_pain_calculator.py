from harcoded_data import instruments, open_interests

# Aisolate the logic of the funbction for testing with harcoded data
def test_max_pain_calculator():

	def get_open_interest(strike_price: int, date: str, direction: str) -> float:
		for data in open_interests[date]:
			if strike_price == data['strike_price'] and direction == data['direction']:
				return data['open_interest']

	def calculate_max_pain(instruments: dict) -> float:
		test_list = []
		for date in instruments:
			aux = {}
			for strike_price in instruments[date]:
				intrinsic_value = 0
				for sp in instruments[date]:
					intrinsic_value += (max(0, strike_price - sp) * get_open_interest(sp, date, 'call')) + (max(0, sp - strike_price) * get_open_interest(sp, date, 'put'))

				if intrinsic_value != 0:
					# Save the strike price and the dollar value for that strike price
					aux[intrinsic_value] = strike_price
			if aux != {}:
				document = {
					'max_pain': aux[min(aux)],
					'dollar_value': min(aux)
				}
				test_list.append(document)

			print(f'max_pain: {aux[min(aux)]}, dollar_value: {min(aux)}')

		return test_list

	response = calculate_max_pain(instruments)

	assert response[0]['max_pain'] == 7800
	assert response[0]['dollar_value'] == 4341862500
	assert response[1]['max_pain'] == 17250
	assert response[1]['dollar_value'] == 2775
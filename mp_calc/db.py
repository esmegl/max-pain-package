import math

ES_HOST = 'http://localhost:9200'

shards = 2;
replicas = 0;
refresh = '1s';

compression = 'best_compression';

default_idx_settings = {
	'index': {
		'number_of_shards': shards,
		'refresh_interval': refresh,
		'number_of_replicas': replicas,
		'codec': compression
	}
};

oi_mapping = {
	'order': 0,
	'index_patterns': [
		'*-oi'
	],
	'settings': default_idx_settings,
	'mappings': {
		'properties': {
			'timestamp': {'type': 'date'},
			'open_interest': {'type': 'double'}
		}
	}
};

trades_mapping = {
	'order': 0,
	'index_patterns': [
		'*-trades'
	],
	'settings': default_idx_settings,
	'mappings': {
		'properties': {
			'direction': {'type': 'keyword'},
			'amount': {'type': 'double'},
			'price': {'type': 'double'},
			'timestamp': {'type': 'date'}
		}
	}
};

max_pain_mapping = {
	'order': 0,
	'index_patterns': [
		'*-max-pain'
	],
	'settings': default_idx_settings,
	'mappings': {
		'properties': {
			'max_pain': {'type': 'double'},
			'dollar_value': {'type': 'double'},
			'timestamp': {'type': 'date'}
		}
	}
}


def es_prefix(instrument_name, kind):
	return f'{instrument_name.lower()}-{kind}'
import json

# get_all() lets you specify the number of results you want to get
def get_all(size: int = 10000) -> dict:
	query = { \
		"query": {
			"match_all": {}
		},
		"size": size
	}
	return query

def get_most_recent(size: int = 1) -> dict:
	query = { \
		"sort": [{"timestamp": "desc"}],
		"size": size
	}

	return query

# Get index in a determined period of time
# Date format: "YYYY-mm-ddTHH:MM:SS.SSSSSS"
def get_within_period(start: str, end: str, size: int = 10000) -> dict:
	query = { \
		"size": size,
		"query": {
			"range": {
				"timestamp": {
					"gte": start,
					"lte": end
				}
			}
		}
	}

	return query

# Get index until a determined period of time
# Date format: "YYYY-mm-ddTHH:MM:SS.SSSSSS"
def get_until(end: str, size: int = 10000) -> dict:
	query = { \
		"size": size,
		"query": {
			"range": {
				"timestamp": {
					"lte": end
				}
			}
		}
	}

	return query

# Get results that matches the nearest time (before and after)
# for a given timestamp, or given a period (start and end)
def get_nearest_time(start: str, end: str) -> dict:
	query = { \
		"size": 0,
		"aggs": {
			"above": {
				"filter": {
					"range": {
						"timestamp": {
							"gt": start
						}
					}
				},
				"aggs": {
					"TopDocument": {
						"terms": {
							"field": "timestamp",
							"size": 1,
							"order": {
								"_key": "asc"
							}
						},
						"aggs": {
							"documents": {
								"top_hits": {
									"size": 1
								}
							}
						}
					}
				}
			},
			"below":{
				"filter": {
					"range": {
						"timestamp": {
							"lt": end
						}
					}
				},
				"aggs": {
					"TopDocument": {
						"terms": {
							"field": "timestamp",
							"size": 1,
							"order": {
								"_key": "desc"
							}
						},
						"aggs": {
							"documents": {
								"top_hits": {
									"size": 1
								}
							}
						}
					}
				}
			}
		}
	}
	return query
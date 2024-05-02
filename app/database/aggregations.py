def today_spending(start, end):
    pipeline = [
        {
            '$match': {
                'date': {'$gte': start, '$lt': end},
                'type': 'expense'
            }
        }, {
            '$group': {
                '_id': None,
                'spends': {
                    '$sum': '$amount'
                }
            }
        }, {
            '$project': {
                'spends': 1,
                '_id': 0
            }
        }
    ]
    return pipeline

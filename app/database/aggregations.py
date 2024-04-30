from datetime import datetime,timedelta

start = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
end = start + timedelta(days=1)

today_spending = [
    {
        '$match': {
            'date': {'$gte':start, '$lt':end},
            'type': 'expense'
        }
    }, {
        '$group': {
            '_id': None,
            'spends': {
                '$sum': '$amount'
            }
        }
    },{
        '$project': {
            'spends': 1,
            '_id': 0
        }
    }
]
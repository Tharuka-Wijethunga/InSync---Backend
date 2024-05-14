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

def sumOfAllExpenses(userID,currentMonth):
    pipeline = [
        {
            '$match': {
                'userID': userID,
                'category': {
                    '$ne': 'Income'
                },
                '$expr': {
                    '$regexMatch':{
                        'input': '$date',
                        'regex': currentMonth,
                        'options': 'i'
                    }
                }
            }
        },
        {
            '$group': {
                '_id': None,
                'totalAmount': {
                    '$sum': '$amount'
                }
            }
        }
    ]
    return pipeline

def getGroupCategorySum(userID,currentMonth):
    pipeline =[
        {
            '$match': {
                'userID': userID,
                'category': {
                    '$ne': 'Income'
                },
                '$expr': {
                    '$regexMatch': {
                        'input': '$date',
                        'regex': currentMonth,
                        'options': 'i'
                    }
                }
            }
        }, {
            '$group': {
                '_id': '$category',
                'sum': {
                    '$sum': '$amount'
                }
            }
        }
    ]
    return pipeline


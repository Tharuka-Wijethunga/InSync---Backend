def today_spending(start, end, userID):
    pipeline = [
        {
            '$match': {
                'userID': userID,
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


def getRecordsByUserID(userID):
    pipeline =[
        {
            '$match': {
                'userID': userID
            }
        },
        {
            '$project': {
                '_id': 0
            }
        }
    ]
    return pipeline


def DailyRecordsGroupByCategory(userID):
    pipeline = [
        {
            '$match': {
                'userID': userID
            }
        }, {
            '$group': {
                '_id': {
                    'date': '$date',
                    'category': '$category'
                },
                'totalAmount': {
                    '$sum': '$amount'
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'Date': '$_id.date',
                'Category': '$_id.category',
                'Amount': '$totalAmount'
            }
        }
    ]
    return pipeline

def GetAllUsersInfo():
    pipeline = [
        {
            '$project': {
                '_id': 0,
                'userID': {
                    '$toString': '$_id'
                },
                'gender': '$gender',
                'incomeRange': '$incomeRange',
                'car': '$car',
                'bike': '$bike',
                'threeWheeler': '$threeWheeler',
                'none': '$none',
                'occupation': '$occupation'
            }
        }
    ]
    return pipeline

def AllUsersDailyRecordsGroupByCategory():
    pipeline = [
        {
            '$group': {
                '_id': {
                    'userID': '$userID',
                    'date': '$date',
                    'category': '$category'
                },
                'totalAmount': {
                    '$sum': '$amount'
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'userID': '$_id.userID',
                'Date': '$_id.date',
                'Category': '$_id.category',
                'Amount': '$totalAmount'
            }
        }
    ]
    return pipeline

def getAccountsByUserID(user_id):
    pipeline = [
        {
            '$match': {
                'userID': user_id
            }
        }
    ]
    return pipeline

def AllUsersID():
    pipeline = [
        {
            '$group': {
                '_id': '$userID',
                'count': {
                    '$sum': 1
                }
            }
        }, {
            '$match': {
                'count': {
                    '$gt': 3
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'userID': '$_id'
            }
        }
    ]
    return pipeline
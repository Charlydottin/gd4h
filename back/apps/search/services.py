
def build_query(key, value, args_date, args_range):
    '''given key,value and fieldtypes list 
    return the query elements
    '''
    #date and range values
    if key in args_date or key in args_range:
        if "," in value:
            try:
                from_, to_ = value.split(",")
                return {"range": 
                        {key:  {
                            "gt": from_, 
                            "lte": to_
                        }}}
            except ValueError:
                # here 2 strategies: 
                # - consider that [value , (MAX or NOW)] (publication, updated)
                if key in args_date:
                    return {"range":{key :{"gte": value}}}  
                else:    
                # - find exact match (impact, level)
                    return {"match": {key: value}}
    #int and string
    else:
        try:
            if " " in value.strip():
                # be carefull this is returning a doc at each match and not unique documents
                return {"terms": {key: value.split(" ")}}
            else:
                # in case type is a string we could also use terms
                return {"match": {key: value}}
        except ValueError:
            return {"match": {key : value}}
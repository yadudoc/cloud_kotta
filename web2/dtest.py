#!/usr/bin/env python
from boto.dynamodb2.fields import HashKey
from boto.dynamodb2.table import Table
import boto.dynamodb2 as ddb
##################################################################
# Update job information in dynamodb
##################################################################
def dynamodb_update(table, data):
    #print "Updating db with : {0}".format(data)
    return table.put_item(data=data, overwrite=True)


##################################################################
# Get job information from dynamodb
##################################################################
def get_job(request, job_id):
    dyntable = request.app.config['dyno.conn']
    try:
        item = dyntable.get_item(job_id=job_id)
    except ItemNotFound:
        return "The requested job_id was not found in the jobs database"
        raise
    return item

##################################################################
# Update job information in dynamodb
##################################################################
def dynamodb_get(table, job_id):
        return table.get_item(job_id=job_id)

##################################################################
# Update job information in dynamodb
##################################################################

def connect_to_db(app, table_name, hashkey):
    dyno = Table(table_name,
                 schema=[HashKey(hashkey)],
                 connection=ddb.connect_to_region(app.config['dynamodb.region'],
                                                  aws_access_key_id=app.config['keys.key_id'],
                                                  aws_secret_access_key=app.config['keys.key_secret'],
                                                  security_token=app.config['keys.key_token']))
    return dyno



def test_1():
    import config_manager as cm
    import time
    import uuid
    app = cm.load_configs("production.conf")
    uid = str(uuid.uuid1())

    
    data = {"job_id"           : uid,
            "username"         : "yadu",
            "jobtype"          : "doc2vec",
            "inputs"           : [{"src": "https://s3.amazonaws.com/klab-jobs/inputs/test.txt", "dest": "test.txt" }],
            "outputs"          : [{"src": "doc_mat.pkl",  "dest": "klab-jobs/outputs/{0}/doc_mat.pkl".format(uid)},
                                  {"src": "word_mat.pkl", "dest": "klab-jobs/outputs/{0}/word_mat.pkl".format(uid)},
                                  {"src": "mdl.pkl",      "dest": "klab-jobs/outputs/{0}/mdl.pkl".format(uid)}],
            "submit_time"      : int(time.time()),
            "status"           : "pending"
    }
    uid = "27013a48-9164-11e5-a61b-0edd34be4cf3"
    #dynamodb_update(app.config["dyno.conn"], data)
    dynamodb_get(app.config["dyno.conn"], uid)


def find_all_users(app):
    
    table_name = app.config['dynamodb.turing_users']
    hashkey    = "user_id"
    dyno = Table(table_name,
                 schema=[HashKey(hashkey)],
                 connection=ddb.connect_to_region(app.config['dynamodb.region'],
                                                  aws_access_key_id=app.config['keys.key_id'],
                                                  aws_secret_access_key=app.config['keys.key_secret'],
                                                  security_token=app.config['keys.key_token']))
    
    try:
        results = dyno.scan()
    except ddb.exceptions.ItemNotFound:
        return None

    return results



def test_2():
    import time
    import config_manager as cm
    app = cm.load_configs("production.conf")

    results = {}
    users = find_all_users(app)
    for user in users:
        name = user["name"]
        all_jobs = app.config["dyno.conn"].scan(i_user_id__eq=user["user_id"])
        
        results[name] = {"Prod" : {"count" : 0,
                                   "walltime" : 0},
                         "Test" : {"count" : 0,
                                   "walltime" : 0}}
        
        count = 0
        for j in all_jobs:
            print j["queue"], j["walltime"]
            if j["walltime"] :
                results[name][j["queue"]]["walltime"] += j["walltime"]
            results[name][j["queue"]]["count"]    += 1
        time.sleep(60)

    for user in results:
        
        print "{0} Prod_count:{1} Prod_wtime:{2} Test_count:{3} Test_wtime:{4}".format(user,
                                                                                       results[user]["Prod"]["count"],
                                                                                       results[user]["Prod"]["walltime"],
                                                                                       results[user]["Test"]["count"],
                                                                                       results[user]["Test"]["walltime"])



import cPickle as pickle
def pickle_to_file(fname, obj):
    with open(fname, 'wb') as handle:
        pickle.dump(obj, handle)

def pickle_load_from_file(fname):
    with open(fname, 'rb') as handle:
        return pickle.load(handle)

def test_3():
    import time
    import config_manager as cm
    app = cm.load_configs("production.conf")

    results = []

    all_jobs = app.config["dyno.conn"].scan()

    
    for job in all_jobs:
        print job
        results.extend([job])

    pickle_to_file("All_jobs.pickle", results)
    return
    
def count_jobs_per_user():
    data  = pickle_load_from_file("All_jobs.pickle")
    user_count = {'Total' : {'count' : 0,
                             'Prod_hrs' : 0,
                             'data_hrs' : 0,
                             'Test_hrs' : 0}
              }
    
    for row in data:        
        u = row['username']
        if row['username'] not in user_count:
            user_count[u] = {'count' : 0,
                             'Prod_hrs' : 0,
                             'data_hrs' : 0,
                             'Test_hrs' : 0}
        user_count[u]['count']          += 1
        user_count['Total']['count']    += 1
        user_count[u]['data_hrs']       += int(row.get('z_stagein_dur', 0)) + int(row.get('z_stageout_dur', 0))
        user_count['Total']['data_hrs'] += int(row.get('z_stagein_dur', 0)) + int(row.get('z_stageout_dur', 0))

        if row['queue'] == 'Prod':
            user_count[u]['Prod_hrs'] += int(row.get('z_processing_dur', 0))
            user_count['Total']['Prod_hrs'] += int(row.get('z_processing_dur', 0))
        else:
            user_count[u]['Test_hrs'] += int(row.get('z_processing_dur', 0))
            user_count['Total']['Test_hrs'] += int(row.get('z_processing_dur', 0))
        
        #print row['inputs'], row['outputs']

    print "{0:44} | {1:5} | {2:6} | {3:6} | {4:6}".format("Username", "JobCount", "ProdHrs", "TestHrs", "DataMin")
    for u in user_count:
        print "{0:44} | {1:5} | {2:6} | {3:6} | {4:6}".format(u, user_count[u]['count'], user_count[u]['Prod_hrs']/3600,
                                                      user_count[u]['Test_hrs']/3600,
                                                      user_count[u]['data_hrs']/3600
        )


if __name__ == "__main__":
    print "Running Test"
    #test_3()
    count_jobs_per_user()

import mysql.connector
from json import dumps

HOST      = ''
PORT      = ''
DBNAME    = 'workflow'
USER      = ''
PASSWORD  = ''


def printTables(cnx):
    query = 'show tables;'
    cursor = cnx.cursor()
    cursor.execute(query)

    print('\n=== ALL TABLES ===')
    for table in cursor:
        print(str(table[0]))
    print('==================\n')
    cursor.close()

def update_task_to_running(cnx:mysql.connector.MySQLConnection, job_id):
    query = f"UPDATE workflows SET task_status='running' WHERE job_id='{job_id}'"
    cursor = cnx.cursor()
    cursor.execute(query)
    cursor.close()

def get_pending_tasks(cnx:mysql.connector.MySQLConnection):
    query = f"SELECT * FROM workflows WHERE task_status='pending';"
    cursor = cnx.cursor()
    cursor.execute(query)

    all_pending = []

    for row in cursor:
        all_pending.append(row)

    cursor.close()

def insert_sample_data(cnx:mysql.connector.MySQLConnection, job_id=None):
    # job_id = '1234567890'
    # job_id = '0987654321'
    # job_id = '6547839201'
    workflow = 'pdb2pqr;apbs'
    workflow_status = 'pending'
    current_task = 0
    task_status = 'pending'
    task_params = [{
        "DEBUMP"        : "atomsnotclose",
        "FF"            : "parse",
        "FFOUT"         : "internal",
        "INPUT"         : "makeapbsin",
        "OPT"           : "optimizeHnetwork",
        # "PDBID"         : "1abf",
        "PDBID"         : "1a1p",
        # "PDBID"         : pdb_id,
        "PDBSOURCE"     : "ID",
        "PH"            : "7.0",
        "PKACALCMETHOD" : "propka"
    },
    {   
        u'bcfl': u'sdh',
        u'calcenergy': u'total',
        u'calcforce': u'no',
        u'cgcent': u'mol',
        u'cgcentid': 1,
        u'cglenx': 42.6292,
        u'cgleny': 33.078599999999994,
        u'cglenz': 25.117499999999996,
        u'charge0': u'',
        u'charge1': u'',
        u'charge2': u'',
        u'chgm': u'spl2',
        u'conc0': u'',
        u'conc1': u'',
        u'conc2': u'',
        u'dimenx': 97,
        u'dimeny': 65,
        u'dimenz': 65,
        u'fgcent': u'mol',
        u'fgcentid': 1,
        u'fglenx': 42.6292,
        u'fgleny': 33.078599999999994,
        u'fglenz': 25.117499999999996,
        u'gcent': u'molecule',
        u'glenx': 42.6292,
        u'gleny': 33.078599999999994,
        u'glenz': 25.117499999999996,
        u'hiddencheck': u'local',
        u'mol': u'1',
        u'ofrac': 0.1,
        u'output_scalar': [   u'writepot'],
        u'pdb2pqrid': job_id,
        u'pdie': 2,
        u'pdimex': 1,
        u'pdimey': 1,
        u'pdimez': 1,
        u'radius0': u'',
        u'radius1': u'',
        u'radius2': u'',
        u'sdens': 10,
        u'sdie': 78.54,
        u'solvetype': u'lpbe',
        u'srad': 1.4,
        u'srfm': u'smol',
        u'swin': 0.3,
        u'temp': 298.15,
        u'type': u'mg-auto',
        u'writeformat': u'dx'
    }]
    query = f"INSERT INTO workflows VALUES ('{job_id}', '{workflow}', '{workflow_status}', {current_task}, '{task_status}', '{dumps(task_params)}');"
    # query = f"INSERT INTO workflows VALUES ('{job_id}', '{workflow}', {current_task}, '{task_status}', '{[{},{}]}');"

    cursor = cnx.cursor()
    cursor.execute(query)
    cursor.close()

if __name__ == "__main__":
    cnx = mysql.connector.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        database=DBNAME
    )

    # printTables(cnx)
    insert_sample_data(cnx, '0987654321')
    insert_sample_data(cnx, '6543782901')
    # get_pending_tasks(cnx)
    # update_task_to_running(cnx, '1234567890')

    cnx.commit()
    cnx.close()
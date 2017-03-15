# tripsql.py
""" TripSql
"""
import csv
import MySQLdb


class TripSql(object):
    def __init__(self, config):
        self.mask = config['tripwire']['mask']
        self.db_con = MySQLdb.connect(**config['mysql_tripwire'])
        self.cursor = self.db_con.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_con.close()

    def _build_edges(self):
        edges = []
        query = """SELECT id, systemID, connectionID, signatureID, sig2ID, type, sig2Type, life, mass,
        DATE_FORMAT(lifeTime, '%Y-%m-%d %T'), DATE_FORMAT(lifeLeft, '%Y-%m-%d %T'), DATE_FORMAT(time, '%Y-%m-%d %T')
        FROM signatures WHERE life IS NOT NULL AND connectionID > 0 AND type <> 'GATE'
        """
        if self.mask:
            query += " AND mask = {}".format(self.mask)
        self.cursor.execute(query)
        result = self.cursor.fetchall()

        for row in result:
            (sys_id, source, target, source_sig, target_sig, source_whcode, target_whcode,
             life, mass, time_created, time_left, last_modified) = row
            if source_whcode not in ('???', 'K162'):
                label = source_whcode
            else:
                label = target_whcode
            edge = row + (label, 'Undirected')
            edges.append(edge)

        return edges

    def output_edges(self, output_path):
        result = self._build_edges()
        with open(output_path, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['id', 'source', 'target', 'sourceSig', 'targetSig', 'sourceWhcode', 'targetWhcode',
                             'life', 'mass', 'timeCreated', 'timeLeft', 'lastModified', 'label', 'type'])
            writer.writerows(result)

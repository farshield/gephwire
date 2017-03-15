# buildnodes.py
import os

import csv
import MySQLdb
import yaml


class BuildNodes(object):
    def __init__(self, config):
        self.config = config
        self.db_con = MySQLdb.connect(**self.config['mysql_sde'])
        self.cursor = self.db_con.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_con.close()

    @staticmethod
    def _compute_security(security):
        if security < 0:
            security_format = "{:.2f}".format(security)
        elif 0 <= security <= 0.1:
            security_format = "0.1"
        else:
            security_format = "{:.1f}".format(security)
        return security_format

    def _system_list(self):
        query = """
        SELECT
            solarSystemID AS systemID,
            solarSystemName AS systemName,
            mapSolarSystems.constellationID,
            mapConstellations.constellationName,
            mapSolarSystems.regionID,
            mapRegions.regionName,
            security
        FROM mapSolarSystems
        LEFT JOIN mapConstellations ON mapSolarSystems.constellationID=mapConstellations.constellationID
        LEFT JOIN mapRegions ON mapSolarSystems.regionID=mapRegions.regionID LIMIT 10"""
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def _build_nodes(self):
        nodes = []
        for row in self._system_list():
            (system_id, system_name, constellation_id, constellation_name, region_id, region_name, security) = row

            # get wormhole class
            wormhole_class = 0
            for location_id in (system_id, constellation_id, region_id):
                query = "SELECT wormholeClassID FROM mapLocationWormholeClasses WHERE locationID=%s"
                self.cursor.execute(query, (location_id, ))
                result = self.cursor.fetchone()
                if result:
                    wormhole_class = result[0]
                    break

            # type
            if wormhole_class == 7:
                system_type = "High-Sec"
            elif wormhole_class == 8:
                system_type = "Low-Sec"
            elif wormhole_class in [0, 9, 10, 11]:
                system_type = "Null-Sec"
            else:
                system_type = "Wormhole"

            # security for pretty print
            security_formatted = self._compute_security(security)

            # comment
            comment = None
            if wormhole_class >= 14:
                comment = "Drifter"
            elif wormhole_class == 13:
                comment = "Frighole"
            elif wormhole_class == [0, 10, 11]:
                comment = "Jove"
            else:
                if "J0" == system_name[:2]:
                    comment = "Shattered"

            node = (system_id, system_name, constellation_id, constellation_name, region_id, region_name,
                    system_type, wormhole_class, security_formatted, comment if comment else 'None')
            nodes.append(node)
        return nodes

    def output_nodes(self, output_path):
        result = self._build_nodes()
        with open(output_path, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['id', 'label', 'constellationID', 'constellationName', 'regionID', 'regionName',
                             'type', 'class', 'security', 'comments'])
            writer.writerows(result)


def main():
    basedir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(basedir, 'config.yaml')) as config_file:
        config = yaml.safe_load(config_file)
    with BuildNodes(config) as build_nodes:
        build_nodes.output_nodes(os.path.join(basedir, 'nodes.csv'))

if __name__ == "__main__":
    main()

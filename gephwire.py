# gephwire.py
""" Gephwire
"""
import os
import yaml
from utils.tripsql import TripSql


def main():
    basedir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(basedir, 'config.yaml')) as config_file:
        config = yaml.safe_load(config_file)

    with TripSql(config) as tripsql:
        tripsql.output_edges('edges.csv')

if __name__ == "__main__":
    main()

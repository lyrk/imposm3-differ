#!/usr/bin/env python

import argparse
import urllib
import json
import os
import subprocess
import logging
from datetime import date


def _get_current_diff_id():
	timedelta = date.today() - date(2012, 9, 12)
	current_id = timedelta.days
	return current_id


def download_diff(diff_id, config):
	base_url = "http://planet.osm.org/replication/day/{AAA}/{BBB}/{CCC}.{suffix}"
	(AAA, BBB, CCC) = map(''.join, zip(*[iter('{0:09d}'.format(diff_id))]*3))
	url_state = base_url.format(AAA=AAA, BBB=BBB, CCC=CCC, suffix="state.txt")
	url_osc = base_url.format(AAA=AAA, BBB=BBB, CCC=CCC, suffix="osc.gz")
	
	state_download_path = os.path.join(config["download_path"], "%s.state.txt" % diff_id)
	diff_download_path = os.path.join(config["download_path"], "%s.osc.gz" % diff_id)

	logging.info("Downloading diff file (id %s)" % diff_id)
	statefile = urllib.urlopen(url_state)
	with open(state_download_path, "wb") as f:
		f.write(statefile.read())
	statefile.close()

	difffile = urllib.urlopen(url_osc)
	with open(diff_download_path, "wb") as f:
		f.write(difffile.read())
	difffile.close()

	return diff_download_path, state_download_path


def import_diff(diff_path, state_download_path, config):
	logging.info("Importing with imposm")
	imposm_config_path = config["imposm_config_path"]
	subprocess.call([config["imposm_path"], "diff", "--config=%s" % imposm_config_path, diff_path])

	logging.info("Cleaning up")
	os.remove(diff_path)
	os.remove(state_download_path)


if __name__ == "__main__":
	logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

	parser = argparse.ArgumentParser(description="Simple tool for downloading and processing OSM diffs for imposm 3.")
	parser.add_argument("--config", default="differ.conf.json", help="Path to the config. An example is located in default.conf.json")
	parser.add_argument("--diffnumber", type=int, help="If you don't want to download the newest diff, specify the diff number here.")
	args = parser.parse_args()

	with open(args.config, "r") as configfile:
		config = json.load(configfile)

	if args.diffnumber == None:
		diff_path, state_download_path = download_diff(_get_current_diff_id(), config)
	else:
		diff_path, state_download_path = download_diff(args.diffnumber, config)

	import_diff(diff_path, state_download_path, config)

import os
import shutil
import logging
import argparse
import tempfile
import glob

from cliff.command import Command
from builder.converter.converter import convert_to_xml


class Test(Command):
    """
    Spits out the generated xmls for input yaml(s) in the configurable out folder
    """
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = argparse.ArgumentParser(description="Parser")
        parser.add_argument("yaml",
                            type=str,
                            nargs="+",
                            help="Path to the view yaml file or directory")
        parser.add_argument("-o",
                            "--out-dir",
                            type=str,
                            dest="out_dir",
                            default=None,
                            help="Path to XML output dir. Default: Temporary directory")
        return parser

    def take_action(self, parsed_args):
        out_dir = parsed_args.out_dir or tempfile.mkdtemp()
        if os.path.isdir(out_dir):
            shutil.rmtree(out_dir, ignore_errors=True)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        for yaml_location in parsed_args.yaml:
            if os.path.isdir(yaml_location):
                yaml_files = glob.glob(os.path.join(yaml_location, '*.yml'))
            else:
                yaml_files = [yaml_location]
            for yaml_filename in yaml_files:
                self.log.debug("Testing view file %s" % yaml_filename)
                with open(os.path.join(yaml_filename), 'r') as yaml_file:
                    yaml = yaml_file.read()
                    self.log.debug(yaml)

            try:
                xmls = convert_to_xml(yaml)
            except Exception as e:
                raise(e)
            if isinstance(xmls[0], str):
                name, xml = xmls
                with open(os.path.join(out_dir, name + ".xml"), 'wb') as xml_file:
                    xml_file.write(xml)
            else:
                for name, xml in xmls:
                    with open(os.path.join(out_dir, name + ".xml"), 'wb') as xml_file:
                        xml_file.write(xml)
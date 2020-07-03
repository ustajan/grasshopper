# This script prepares a GDML file which can be run by Grasshopper.
import subprocess
import xml.etree.ElementTree as ET

class GrasshopperPreprocess:
    """
    Class to handle requests to generate GDML files.
    """
    def __init__(self):
        self.default_filename = "default.gdml"
        self.gen_filename = "grasshopper_sim.gdml"

    @staticmethod
    def get_element_tree(gdml_filename):
        """
`
        :param gdml_filename: The GDML filename string to parse
        :return:
        """
        GDML_tree = ET.parse(gdml_filename)
        GDML_root = GDML_tree.getroot()
        for child in GDML_root:
            print(child.tag, child.attrib)
            for subchild in child:
                print(type(subchild.tag), type(subchild.attrib))
                print(subchild.tag, subchild.attrib)
        return 0

    def start_subprocess(self, gdml_filename, data_filename):
        """
        Starts a subprocess from the python module
        which can start a Grasshopper subprocess.
        :param gdml_filename: The GDML filename created
        :param data_filename: The requested data filename
        :return: Starts a process if 0, not if 1
        """
        subprocess.run(["grasshopper", gdml_filename, data_filename])


if __name__ == '__main__':
    preprocess_operator = GrasshopperPreprocess()
    preprocess_operator = GrasshopperPreprocess.get_element_tree(gdml_filename="neutron.gdml")
    # preprocess_operator.start_subprocess(gdml_filename="neutron.gdml", data_filename="neutron_test")
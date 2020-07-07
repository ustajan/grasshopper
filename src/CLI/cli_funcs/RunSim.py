#!/venv/bin/python3.7
import os
from os import listdir
from os.path import isfile, join
import subprocess
from pyfiglet import Figlet
from terminaltables import SingleTable, ascii_table, AsciiTable
import json


class RunSim:
    """
    Class for functions associated with grasshopper shell script list sensors feature
    """
    def __init__(self):
        self.questions = ["How many unique materials are used in the simulation? ",
                          "What is particle type being used? (proton, neutron, electron, photon...)",
                          "How many kgs of that item are there? [kg]",
                          "What is the density of that item? [kg/m^3]"
                          ]

    def get_sim(self):
        """
        This function prepares the questions for populating a GDML file.
        :return:
        """
        answers = self.set_questions()
        return 0

    def set_questions(self):
        """
        Method to query the user to set answers to a variety of questions.
        :return:
        """
        answer_list = []
        print(' This tool will ask you a set of questions to generate a simulation input. \n')
        while True:
            try:
                for question in self.questions:
                    print(question)
                    q_answer = input()
                    answer_list.append(q_answer)
            except TypeError:
                print("Please try again")
                continue
            except ValueError:
                print("Please try again")
                continue
            else:
                break

        # TODO: work this out to utilize the *.json which drives CLI input
        return answer_list

    def generate_input_GDML(self):
        """

        :return:
        """
        pass

    def start_grasshopper_sim(self):
        """

        :return:
        """
        pass

    def run_GDML_sims(self):
        """
        Runs all GDML files under simulation_GDML/
        :return:
        """
        GDML_file_path = "./sim_generation/simulation_GDML/"
        GDML_files = [f for f in listdir(GDML_file_path) if isfile(join(GDML_file_path, f))]
        print(GDML_files)
        for GDML_file in GDML_files:
            subprocess.call(["grasshopper", GDML_file_path + str(GDML_file), GDML_file_path + str(GDML_file)+"data"])
        return 0

    def run_json_sims(self):
        """
        Runs all JSON files under simulation_json/
        :return:
        """
        JSON_file_path = "./sim_generation/simulation_json/"
        json_files = [f for f in listdir(JSON_file_path) if isfile(join(JSON_file_path, f))]
        print(json_files)
        return 0

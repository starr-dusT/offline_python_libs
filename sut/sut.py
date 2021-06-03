import os
import yaml
import subprocess
from subprocess_tee import run
import time

class Sut:
    def __init__(self, config_location):
        self.config = yaml.safe_load(open(config_location))
        self.start_dir = os.getcwd()
        self.old_hash = self.__get_hash()

    def __get_hash(self):
        os.chdir(self.config["repo_location"])
        current_hash = subprocess.getoutput("git rev-parse HEAD")
        os.chdir(self.start_dir)
        return current_hash

    def __create_env(self, current_hash):
        output_location = os.path.join(self.config["output_directory"], current_hash)
        clone_location = os.path.join(output_location, ".tmp")
        try:
            os.makedirs(clone_location)
        except:
            print("WARNING: overwriting previous results")
            os.rmdir(clone_location)
            os.makedirs(clone_location)
        subprocess.run(['git', 'clone', '--quiet',
                        self.config["repo_location"], clone_location])
        return output_location

    def __run_commands(self, output_location):
        print("Running commands...")
        os.chdir(os.path.join(output_location, ".tmp"))
        for job in self.config["jobs"].keys():
            print(job + ":\n\n")
            command = self.config["jobs"][job] 
            output = run(command)
            with open(os.path.join(output_location, job + ".txt"), 'w') as f:
                print(output, file=f)
        os.chdir(self.start_dir)

    def __clear_output(self):
        # for windows
        if os.name == 'nt':
            _ = os.system("cls")
        # for mac/linux
        else:
            _ = os.system("clear")

    def run(self):
        first_cycle = True
        while 1:
            if first_cycle == True:
                print("Waiting for changes...")
                first_cycle = False
            current_hash = self.__get_hash()
            if self.old_hash != current_hash:
                print("Detected changes...")
                output_location = self.__create_env(current_hash)
                self.__run_commands(output_location)
                self.old_hash = current_hash
                first_cycle = True
                input("Done... Press enter to continue")
                self.__clear_output()
                continue
            time.sleep(5)

if __name__ == '__main__':
    config_location = r"/home/tstarr/devel/python/sut/examples/config.yaml"
    tester = Sut(config_location)
    tester.run()

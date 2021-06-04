import os
import yaml
import subprocess
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

    def __run_commands(self):
        print("Running commands...")
        os.chdir(self.config["repo_location"])
        for job in self.config["jobs"].keys():
            print(job + ":\n\n")
            command = self.config["jobs"][job] 
            subprocess.run(command.split(" "))
            print("\n\n")
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
                self.__run_commands()
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

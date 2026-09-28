import json
from pathlib import Path


class SecurityGroupSimulator:

    def __init__(
        self,
        file_path="data/simulated_live_cloud.json"
    ):
        self.file_path = Path(file_path)
        self.load()

    def load(self):
        with open(self.file_path, "r") as file:
            self.cloud_data = json.load(file)

    def save(self):
        with open(self.file_path, "w") as file:
            json.dump(self.cloud_data, file, indent=4)

    def add_public_database_rule(self):
        for sg in self.cloud_data["security_groups"]:
            if sg["id"] == "sg-db":
                rule = {
                    "protocol": "tcp",
                    "port": 3306,
                    "source": "0.0.0.0/0"
                }

                if rule not in sg["rules"]:
                    sg["rules"].append(rule)
                    self.save()
                    print("Public database rule added.")
                else:
                    print("Rule already exists.")

                return

        print("Security group sg-db not found.")

    def remove_public_database_rule(self):
        for sg in self.cloud_data["security_groups"]:
            if sg["id"] == "sg-db":
                rule = {
                    "protocol": "tcp",
                    "port": 3306,
                    "source": "0.0.0.0/0"
                }

                if rule in sg["rules"]:
                    sg["rules"].remove(rule)
                    self.save()
                    print("Public database rule removed.")
                else:
                    print("Public database rule not found.")

                return

        print("Security group sg-db not found.")

    def show_rules(self):
        for sg in self.cloud_data["security_groups"]:
            if sg["id"] == "sg-db":
                print("\nSecurity Group:", sg["id"])
                print("Current ingress rules:")

                for rule in sg["rules"]:
                    print(
                        f"Protocol: {rule['protocol']}, "
                        f"Port: {rule['port']}, "
                        f"Source: {rule['source']}"
                    )


def main():
    simulator = SecurityGroupSimulator()

    while True:
        print("\n===== AeroDrift AWS Simulator =====")
        print("1. Show database security-group rules")
        print("2. Expose database port 3306 to Internet")
        print("3. Remove public database rule")
        print("4. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            simulator.load()
            simulator.show_rules()

        elif choice == "2":
            simulator.add_public_database_rule()

        elif choice == "3":
            simulator.remove_public_database_rule()

        elif choice == "4":
            print("Simulator closed.")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
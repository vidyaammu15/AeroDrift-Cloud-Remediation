import json


class MockAWSCollector:

    def __init__(self, file_path="data/mock_cloud.json"):
        self.file_path = file_path

    def collect(self):
        with open(self.file_path, "r") as file:
            return json.load(file)


if __name__ == "__main__":
    collector = MockAWSCollector()
    data = collector.collect()

    print("Mock AWS collection successful")
    print("VPCs:", len(data["vpcs"]))
    print("Subnets:", len(data["subnets"]))
    print("Security Groups:", len(data["security_groups"]))
    print("Instances:", len(data["instances"]))
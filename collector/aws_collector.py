import asyncio
import boto3


class AsyncAWSCollector:
    def __init__(self, region="us-east-1"):
        self.ec2 = boto3.client("ec2", region_name=region)

    def get_vpcs(self):
        return self.ec2.describe_vpcs()["Vpcs"]

    def get_subnets(self):
        return self.ec2.describe_subnets()["Subnets"]

    def get_security_groups(self):
        return self.ec2.describe_security_groups()["SecurityGroups"]

    def get_instances(self):
        response = self.ec2.describe_instances()

        instances = []

        for reservation in response["Reservations"]:
            instances.extend(reservation["Instances"])

        return instances

    async def collect(self):
        vpcs, subnets, security_groups, instances = await asyncio.gather(
            asyncio.to_thread(self.get_vpcs),
            asyncio.to_thread(self.get_subnets),
            asyncio.to_thread(self.get_security_groups),
            asyncio.to_thread(self.get_instances)
        )

        return {
            "vpcs": vpcs,
            "subnets": subnets,
            "security_groups": security_groups,
            "instances": instances
        }


if __name__ == "__main__":
    collector = AsyncAWSCollector()

    try:
        data = asyncio.run(collector.collect())

        print("Concurrent AWS collection successful")
        print("VPCs:", len(data["vpcs"]))
        print("Subnets:", len(data["subnets"]))
        print("Security Groups:", len(data["security_groups"]))
        print("Instances:", len(data["instances"]))

    except Exception as e:
        print("AWS collection could not be completed.")
        print(type(e).__name__, "-", e)
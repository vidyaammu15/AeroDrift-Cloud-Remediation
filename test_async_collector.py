import asyncio
from collector.aws_collector import AsyncAWSCollector


async def main():
    collector = AsyncAWSCollector()

    collector.get_vpcs = lambda: [{"VpcId": "vpc-001"}]

    collector.get_subnets = lambda: [
        {"SubnetId": "subnet-public"},
        {"SubnetId": "subnet-private"}
    ]

    collector.get_security_groups = lambda: [
        {"GroupId": "sg-web"},
        {"GroupId": "sg-db"}
    ]

    collector.get_instances = lambda: [
        {"InstanceId": "i-web-001"},
        {"InstanceId": "i-db-001"}
    ]

    data = await collector.collect()

    print("Concurrent collector test successful")
    print("VPCs:", len(data["vpcs"]))
    print("Subnets:", len(data["subnets"]))
    print("Security Groups:", len(data["security_groups"]))
    print("Instances:", len(data["instances"]))


asyncio.run(main())
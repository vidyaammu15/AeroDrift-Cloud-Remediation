
"""Optional AWS connectivity check; safe during unittest discovery."""

import os
import unittest


def check_aws_connection():
    """Connect to AWS only when explicitly requested."""
    import boto3

    ec2 = boto3.client("ec2", region_name="ap-south-1")
    response = ec2.describe_vpcs()

    print("AWS connection successful")
    print("Number of VPCs:", len(response["Vpcs"]))

    for vpc in response["Vpcs"]:
        print("VPC ID:", vpc["VpcId"])


class TestAWSConnectivity(unittest.TestCase):
    @unittest.skipUnless(
        os.environ.get("AERODRIFT_RUN_AWS_TESTS") == "1",
        "Set AERODRIFT_RUN_AWS_TESTS=1 to run live AWS checks",
    )
    def test_aws_connection(self):
        check_aws_connection()


if __name__ == "__main__":
    unittest.main(verbosity=2)

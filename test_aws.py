import boto3

ec2 = boto3.client("ec2", region_name="ap-south-1")

response = ec2.describe_vpcs()

print("AWS connection successful")
print("Number of VPCs:", len(response["Vpcs"]))

for vpc in response["Vpcs"]:
    print("VPC ID:", vpc["VpcId"])
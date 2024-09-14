#!/usr/bin/env python
# -*- coding: utf8 -*-"

import boto3
from botocore.client import ClientError
import requests
import subprocess
import os

# Collecting information about EC2 instance from AWS service

user_data = "http://169.254.169.254/latest/user-data"
meta_data = "http://169.254.169.254/latest/meta-data"
ec2InsDatafile = "ec2InsDatafile"
ec2_params = {
    "Instance ID": "instance-id",
    "Reservation ID": "reservation-id",
    "Public IP": "public-ipv4",
    "Public Hostname": "public-hostname",
    "Private IP": "local-ipv4",
    "Security Groups": "security-groups",
    "AMI ID": "ami-id",
}

# Subprocess was not used, but I assume it's a hint to use it instead of popen
# Also, as we're runnning 3 different commands we can create a function to handle them
def check_os_options(command):
    try:
        result = subprocess.check_output(command, shell=True, text=True).strip()
        return result
    except Exception as e:
        print(f"Error while running command {command} : {e}")
        return None


try:
    with open(ec2InsDatafile, "w") as fh:
        for param, value in ec2_params.items():
            try:
                response = requests.get(meta_data + "/" + value)
                if isinstance(response.text, list):
                    print(response.text + ": is a list")
                    data = " ".join(response.text)
                else:
                    data = param + ":" + response.text
                fh.write(data + "\r\n")
            except Exception as e:
                print(f"Error while making request: {e}")

        os_vers = "grep '^VERSION=' /etc/os-release | cut -d'=' -f2"
        os_name = "grep '^NAME' /etc/os-release | cut -d'=' -f2"
        os_usrs = "grep -E 'bash|sh' /etc/passwd | awk -F : '{print $1}' | xargs echo"

        os_name_val = "OS_NAME:" + check_os_options(os_name)
        os_vers_val = "OS_VERSION:" + check_os_options(os_vers)
        os_usrs_val = "Login able users:" + check_os_options(os_usrs)

        try:
            fh.write(os_name_val + "\r\n")
            fh.write(os_vers_val + "\r\n")
            fh.write(os_usrs_val + "\r\n")
        except:
            print(f"Error during write to file: {e}")
            fh.close()

except OSError as e:
    print(f"Error while opening file for write: {e}")

# Upload file to s3 storage
s3_bucket_name = "new-bucket-e05ab0e0"
s3_conn = boto3.client("s3")

try:
    s3.meta.client.head_bucket(Bucket=s3_bucket_name)

    with (ec2InsDatafile, "r") as fh:
        s3_conn.put_object(
            Bucket=s3_bucket_name,
            Key="system_info" + requests.get(meta_data + "/" + instance_id) + ".txt",
            Body=fh.read(),
        )
    print(
        "File has been uploaded into "
        + s3_bucket_name
        + " S3 bucket with instance_id key."
    )
except ClientError:
    print("Are you sure the destination bucket exist? Check it.")

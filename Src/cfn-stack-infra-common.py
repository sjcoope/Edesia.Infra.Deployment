from __future__ import print_function
import sys
import datetime
import argparse
import boto3
from utility import *
from cfn_utilty import *
from botocore.exceptions import ClientError, WaiterError

# Globals
application_name = "sjcnet-edesia"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stack_name", help="The CFN stack to update")
    parser.add_argument("template", help="The CFN Template to update the stack")
    parser.add_argument("environment", help="The name of the environment to build")
    args = parser.parse_args()

    # Validate and output args
    args.environment = args.environment.lower()
    log('ARGS: ' + str(args))

     # Check if stack exists, if not create it
    if(stack_exists(args.stack_name)==False):
        log('Stack does NOT exist')
        create_stack(
                args.stack_name, 
                args.template, 
                args.environment)

        log('Stack successfully created')
    else:
        log('Stack Exists')

        # Create change set name
        changeset_name = application_name + "-Changeset-"+datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
        log("ChangeSet Name: " + changeset_name)

        # Create change set and check status
        if create_change_set(args.stack_name, args.template, changeset_name):
            status=get_change_set_status(args.stack_name, changeset_name)
            log("Status: " + status)

            if(status=="Success"):
                if execute_change_set(args.stack_name, changeset_name):
                    log("Stack update complete")
                else:
                    log("Stack update FAILED")
                    sys.exit(1)
            else:
                if(status=="NoChanges"):
                    log("No changes in CF template.")
                else:
                    sys.exit(1)
        else:
            log("Create ChangeSet FAILED")
            sys.exit(1)

    #delete_s3_bucket(temp_bucket_name)

if __name__ == "__main__":
    main()
# Needed packages
import os
import subprocess
import getpass
import json

current_user = getpass.getuser()   # Get the user running the script
# Define the directory path in which a directory will be created
# to store text files with the results obtained from this script.
directory_path = f'/home/{current_user}/Desktop/Cloud_Results'  # It will be in the Desktop

# Create the directory if it doesn't already exist
if not os.path.exists(directory_path):
    os.makedirs(directory_path)

# Change the current working directory to the new directory
# It is important to change the directory because synchronization with the bucket will be performed.
# This way, files will not be synchronized from the machine to S3.
os.chdir(directory_path)

def logs():  # Fuction to download the CLoudTrails and look events in them.
# Receive user input for the S3 bucket name and AWS profile
# The bucket name will be without the S3. E.g., flaws2-logs
    bucket_name = input("Enter the name of the S3 bucket to sync:\n")
    aws_profile = input("Enter the name of the AWS profile to use:\n")



# Command to synchronize the bucket.
    aws_cli_cmd = ['aws', 's3', '--profile', aws_profile, 'sync', f's3://{bucket_name}', '.']

# Send the command to be executed by the system using subprocess
    subprocess.run(aws_cli_cmd, check=True)
    gunzip_command = "find . -type f -exec gunzip {} \;"  # Unzip the downloaded JSON files.
    cat_jq_command = "find . -type f -exec cat {} \; | jq '.'"

# Execute the commands using exception handling
    try:
        gunzip_output = subprocess.check_output(gunzip_command, shell=True, stderr=subprocess.STDOUT)
        cat_jq_output = subprocess.check_output(cat_jq_command, shell=True, stderr=subprocess.STDOUT)
        output = gunzip_output + cat_jq_output
    except subprocess.CalledProcessError as e:
        output = e.output

# Write the output to a file. It will store all the events collected.
    with open("output.txt", "w") as f:
        f.write(output.decode())
# Inform the user
    print(f'The logs are stored at {directory_path}, you can see the information in Output.txt')
    decision = "0"
    while decision!='2':  # While the user does not choose that they do not want to review events...
        decision = input("\nDo you want to look an event?\n 1) Yes \n 2) No\n")
        if decision == '1':  # If the user wants to look a particular event
            event_name = input("Please tell the event name\n")  # Ask the event name. E.g, ListBuckets

            #  The following line is the command that will display Event Time, source IP address, User identity,
            #  account ID and other information, from the records and, specifically,
            #  about the event specified by the user.
            cmd = r"find . -type f -exec cat {} \; " \
                  r"| jq -cr '.Records[]|[.eventTime, .sourceIPAddress,.userIdentity.arn,.userIdentity.accountId, " \
                  r".userIdentity.type, .eventName]|@tsv' | sort"
            cmd2 = f"{cmd}| grep {event_name}"
            # Send the output to a text file which name is the event name.
            output_file = f"{event_name}.txt"

            # Write into the file
            with open(output_file, "w") as f:
                subprocess.run(cmd2, shell=True, stdout=f)
                # Inform the user.
            print(f"\nThe logs containing '{event_name}' are stored in '{output_file}'.")


def images():  # Function to look if there are public images in a repository.

    image_profile_name = input("Enter the profile you are going to use\n")
    #  Command to be used.
    aws_cli_cmd = ['aws', 'sts', 'get-caller-identity', '--profile', image_profile_name]
    # Execute the AWS CLI command using subprocess
    aws_cli_output = subprocess.check_output(aws_cli_cmd)
    # Decode the output as JSON
    aws_cli_output_json = json.loads(aws_cli_output)
    # Extract the account ID from the output.
    account_id = aws_cli_output_json['Account']

    loop = " "  # To control the loop
    while loop != '2':
        loop = input("Enter 1 to continue, and 2 to exit\n")
        if loop == '1':
            repository = input("Which repository you want to look?\n")  # The repository is specified by the user.
            aws_cli_cmd = [
                f'aws ecr list-images --repository-name {repository} --registry-id {account_id} --profile {image_profile_name}']
        # Execute the AWS CLI command using subprocess and save output to a file
            output_file = f"{repository}.txt"  # A new file each time the user decides another repository
            with open(output_file, "w") as f:  # Send the output to a text file with the name of the repository.
                try:
                    subprocess.run(aws_cli_cmd, check=True, stdout=f)
                except FileNotFoundError:  # In case the user enters an incorrect profile or repository
                    pass

        # Inform the user
        print("Command output saved to ", output_file)

def content():  # FUnction to list the contents of a bucket
   profile_name = input("Which profile are you using?\n")
   output_file = f"{profile_name}.txt"
   # Open the output file in write mode
   with open(output_file, "w") as f:
       # Run the AWS CLI command with the user input profile and redirect the output to the file
       subprocess.run(["aws", "s3", "--profile", profile_name, "ls"], stdout=f)
       print("The information was sent to ",output_file)

# Starting question to the user.
user_input = " "
while user_input!= '4':
    user_input = input("\nPlease enter your option\n1) See bucket logs\n2) See ECR public images\n3) List S3 contents\n4) Exit\n")
    if(user_input=='1'):
        logs()
    if(user_input=='2'):
        images()
    if(user_input=='3'):
        content()

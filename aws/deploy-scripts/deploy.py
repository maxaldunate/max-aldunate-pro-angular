import boto3
import yaml
import sys
import subprocess

def cfgLoad(filePath):
	cfg = {}
	with open(filePath, 'r') as ymlfile:
		cfg = yaml.load(ymlfile)
	return cfg

def pathBuild(cfg, path, file):
	return cfg['base-dir'] + path + "\\" + file

def runStack(cfg, bucketDeployPackages):
	for st in cfg['stacks']:
		stackFullName = cfg['stack-base-name'] + st['name']
		fullFile = pathBuild(cfg, st['path'], st['template-file'])
		outputDir = pathBuild(cfg, cfg['output-dir-stacks'], st['template-file'])

		print("=======================================================================")
		print("Stack Name: " +  stackFullName)
		print("Stack Path: " +  st['path'])
		print("Stack File: " +  st['template-file'])
		
		print()
		print("$ package command .............")
		cmdPackege = "aws cloudformation package --template-file " + fullFile + \
			" --output-template-file " + fullFile + "-deploy.yaml" + \
			" --s3-bucket " + bucketDeployPackages + " " \
			" --profile " + cfg['profile-user']
		print(cmdPackege)
		print(subprocess.check_output([cmdPackege]))
		

		print()
		print("$ deploy command .............")
		cmdDeploy = "aws cloudformation deploy " + \
        		" --region " + cfg['aws-region'] + \
        		" --template-file " + fullFile + "-deploy.yaml " + \
        		" --stack-name " + stackFullName + \
        		" --capabilities CAPABILITY_IAM " + \
        		" --profile " + cfg['profile-user'] + \
        		" --tags Project=" + cfg['project-tag'] + \
        		" --parameter-overrides TagProject=" + cfg['project-tag']
		print(cmdPackege)

def awsSession(cfg):
	boto3.setup_default_session(profile_name=cfg['profile-user'])
	boto3.setup_default_session(region_name=cfg['aws-region'])

def runPrerequisitesStack(cfg):
	print("===================================================================================")
	print("Prerequisite Stack")
	stackName = cfg['stack-base-name'] + "-prerequisites"
	print("Stack Name: " +  stackName)
	print("Stack File: " +  cfg['prerequisites-stack-file'])
	command = "aws cloudformation deploy " + \
    	" --region " + cfg['aws-region'] + \
    	" --template-file " + cfg['base-dir'] + cfg['prerequisites-stack-file'] + \
    	" --stack-name " + stackName + \
    	" --capabilities CAPABILITY_IAM " + \
    	" --profile " + cfg['profile-user'] + \
    	" --tags Project=" + cfg['project-tag'] + \
    	" --parameter-overrides TagProject=" + cfg['project-tag'] + \
    	" AppName=" + cfg['stack-base-name']
	runShell(command)
	describeCmd = composeStackDescribeCommand(cfg, stackName)
	runShell(describeCmd)


def composeStackDescribeCommand(cfg, stackName):
	return "aws cloudformation  describe-stacks " + \
		" --stack-name " + stackName + \
		" --profile " + cfg['profile-user'] + \
    	" --region " + cfg['aws-region'] + \
    	" > " + cfg['base-dir'] + cfg['output-dir-stacks'] + "\\" + stackName + "-output.json"

def runShell(command):
	print("------------------------------------ starts command -------------------------------")
	print(command)
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	process.wait()
	print(process.returncode)
	print("------------------------------------ end command ----------------------------------")

def main():
	filePath = sys.argv[1]
	cfg = cfgLoad(filePath)
	awsSession(cfg)

	runPrerequisitesStack(cfg)
	#runStack(cfg, bucketDeployPackages)

if __name__ == '__main__':
	main()
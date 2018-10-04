import boto3
import yaml
import sys
import subprocess
import json
from pathlib import Path
import os

def cfgLoad(filePath):
	cfg = {}
	with open(filePath, 'r') as ymlfile:
		cfg = yaml.load(ymlfile)
	return cfg

def pathBuild(cfg, path, file):
	return cfg['base-dir'] + path + "\\" + file

def awsSession(cfg):
	boto3.setup_default_session(profile_name=cfg['profile-user'])
	boto3.setup_default_session(region_name=cfg['aws-region'])

def composeStackDescribeCommand(cfg, fullOutputFile, stackName):
	return "aws cloudformation  describe-stacks " + \
		" --stack-name " + stackName + \
		" --profile " + cfg['profile-user'] + \
    	" --region " + cfg['aws-region'] + \
    	" > " + fullOutputFile

def runShell(command, commandName):
	print("------------------------------------ " + commandName)
	print(command)
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	process.wait()
	print(process.returncode)

def extractOutputs(describeFile, cfgOutFile, stackName, simpleStackName):
	outputDict = {"Outputs": []}
	with open(describeFile, 'r') as f:
		describeDict = json.load(f)
	for st in describeDict["Stacks"]:
		if(st["StackName"]==stackName):
			for out in st["Outputs"]:
				out["StackName"] = simpleStackName
				outputDict["Outputs"].append(out)

	with open(cfgOutFile, 'r') as f:
		data = json.load(f)
	for out in outputDict["Outputs"]:
		data["Outputs"].append(out)
	with open(cfgOutFile, 'w') as fw:
		json.dump(data, fw, ensure_ascii=False, sort_keys=True, indent=2)

def runShellStack(command, cfg, stackName, simpleStackName, cfgOutFile):
	runShell(command, simpleStackName)
	fullOutputFile = pathBuild(cfg, cfg['output-dir-stacks'], stackName + "-output.json")
	runShell(composeStackDescribeCommand(cfg, fullOutputFile, stackName), simpleStackName + " decribe stack ...")
	extractOutputs(fullOutputFile, cfgOutFile, stackName, simpleStackName)

def runPrerequisitesStack(cfg, cfgOutFile):
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
	runShellStack(command, cfg, stackName, "prerequisites", cfgOutFile)
	
def configOutputFileInitialize(cfg):
	cfgOutFile = pathBuild(cfg, cfg['output-dir-stacks'], "\\config-output.json")
	print(cfgOutFile)
	if os.path.isfile(cfgOutFile):
		print("Removing config-output.json file at " + cfgOutFile)
		os.remove(cfgOutFile)
	with open(cfgOutFile, 'w') as f:
		json.dump({"Outputs": []}, f, ensure_ascii=False, sort_keys=True, indent=2)

	return cfgOutFile

def getOutputValue(parametersSource, cfgOutFile, nameParameter):
	oF = {}
	with open(cfgOutFile, 'r') as f:
		oF = json.load(f)

	oneParamSource = {}
	for p in parametersSource:
		if(p['name']==nameParameter):
			oneParamSource = p

	if(oneParamSource=={}):
		return ""

	value = ""
	for out in oF['Outputs']:
		if(out['StackName']==oneParamSource['stackName'] and \
			out['OutputKey']==oneParamSource['outputKey']):
			value = out['OutputValue']
	return value


def runStack(cfg, st, cfgOutFile):
	stackFullName = cfg['stack-base-name'] + "-" + st['name']
	fullFile = pathBuild(cfg, st['path'], st['template-file'])
	outputDir = pathBuild(cfg, cfg['output-dir-stacks'], st['template-file'])

	print("=======================================================================")
	print("Stack Name: " +  stackFullName)
	print("Stack Path: " +  st['path'])
	print("Stack File: " +  st['template-file'])
	
	print()
	print("$ package command .............")
	bk = getOutputValue(st['parameters-source'], cfgOutFile, "bucketDeployPackages")
	cmdPackage = " aws cloudformation package --template-file " + fullFile + \
		" --output-template-file " + fullFile + "-deploy.yaml" + \
		" --s3-bucket " + bk + " " \
		" --region " + cfg['aws-region'] + \
		" --profile " + cfg['profile-user']
	runShell(cmdPackage, st['name'] + " package stack ...")

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
	#runShellStack(cmdDeploy, cfg, stackFullName, st['name'] + " deploy stack ...", cfgOutFile)

def main():
	filePath = sys.argv[1]
	cfg = cfgLoad(filePath)
	awsSession(cfg)
	cfgOutFile = configOutputFileInitialize(cfg)
	runPrerequisitesStack(cfg, cfgOutFile)
	
	for st in cfg['stacks']:
		runStack(cfg, st, cfgOutFile)

if __name__ == '__main__':
	main()
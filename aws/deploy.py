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
	return cfg['dir']['base'] + path + "\\" + file

def awsSession(cfg):
	boto3.setup_default_session(profile_name=cfg['aws']['profile-user'])
	boto3.setup_default_session(region_name=cfg['aws']['aws-region'])

def composeStackDescribeCommand(cfg, fullOutputFile, stackName):
	return "aws cloudformation  describe-stacks " + \
		" --stack-name " + stackName + \
		" --profile " + cfg['aws']['profile-user'] + \
    	" --region " + cfg['aws']['aws-region'] + \
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
	fullOutputFile = pathBuild(cfg, cfg['dir']['output'], stackName + "-output.json")
	runShell(composeStackDescribeCommand(cfg, fullOutputFile, stackName), simpleStackName + " decribe stack ...")
	extractOutputs(fullOutputFile, cfgOutFile, stackName, simpleStackName)

def configOutputFileInitialize(cfg):
	cfgOutFile = pathBuild(cfg, cfg['dir']['output'], "config-output.json")
	ifExistRemoveFile(cfgOutFile)
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

def getValueForOutput(cfgOutFile, stackName, outputKey):
	outFile = {}
	with open(cfgOutFile, 'r') as f:
		outFile = json.load(f)

	for out in outFile['Outputs']:
		if(out['StackName']==stackName and \
			out['OutputKey']==outputKey):
			return out['OutputValue']
	return ""

def setOutputValue(parametersSource, cfgOutFile):
	for pSource in parametersSource:
		if "value" not in pSource:
			pSource["value"] = getValueForOutput(cfgOutFile, pSource["stackName"], pSource["outputKey"])
	return parametersSource

def ifExistRemoveFile(file):
	if os.path.isfile(file):
		print("Removing file at ... " + file)
		os.remove(file)

def runStack(cfg, st, cfgOutFile):
	stackFullName = cfg['project']['stack-base-name'] + "-" + st['name']
	fullFile = pathBuild(cfg, cfg['dir']['stacks'], st['name'] + ".yaml")
	outputDir = pathBuild(cfg, cfg['dir']['output'], st['name'] + ".yaml")
	print()
	print()
	print("=======================================================================")
	print("Stack Name: " +  stackFullName)
	print("Stack File: " +  st['name'] + ".yaml")
	
	ifExistRemoveFile(fullFile + "-deploy.yaml")
	
	if(st['parameters-source'] != None):
		setOutputValue(st['parameters-source'], cfgOutFile)
	
	deployFullFile = fullFile
	if(st["package"]):
		print()
		print("$ package command .............")
		deployFullFile = outputDir + "-deploy.yaml "
		bk = getValueForOutput(cfgOutFile, cfg['packages-deploy-bucket']["stackName"], \
			cfg['packages-deploy-bucket']["outputKey"])
		cmdPackage = " aws cloudformation package --template-file " + fullFile + \
			" --output-template-file " + outputDir + "-deploy.yaml" + \
			" --s3-bucket " + bk + " " \
			" --region " + cfg['aws']['aws-region'] + \
			" --profile " + cfg['aws']['profile-user']
		runShell(cmdPackage, st['name'])

	print()
	print("$ deploy command .............")

	cmdDeploy = "aws cloudformation deploy " + \
    		" --region " + cfg['aws']['aws-region'] + \
    		" --profile " + cfg['aws']['profile-user'] + \
    		" --template-file " + deployFullFile + \
    		" --stack-name " + stackFullName + \
    		" --capabilities CAPABILITY_IAM " + \
    		" --tags Project=" + cfg['project']['tag'] + \
    		" --parameter-overrides TagProject=" + cfg['project']['tag']
	if(st['parameters-source'] != None):
		for pS in st['parameters-source']:
			cmdDeploy = cmdDeploy + " " + pS["name"] + "=" + pS["value"]

	runShellStack(cmdDeploy, cfg, stackFullName, st['name'], cfgOutFile)

def main():
	filePath = sys.argv[1]
	cfg = cfgLoad(filePath)
	awsSession(cfg)
	cfgOutFile = configOutputFileInitialize(cfg)
	
	for st in cfg['stacks']:
		runStack(cfg, st, cfgOutFile)

	print("========================================================================")
	print("===========================      FINISH      ===========================")
	print("========================================================================")

if __name__ == '__main__':
	main()
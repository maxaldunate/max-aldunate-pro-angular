import boto3
import yaml
import sys
import subprocess
import json
from pathlib import Path
import os
import string
import random
import shutil
import time

def cfgLoad(filePath):
	cfg = {}
	with open(filePath, 'r') as ymlfile:
		cfg = yaml.load(ymlfile)
	return cfg

def pathFileBuild(cfg, path, file):
	return pathBuild(cfg, path) + "\\" + file

def pathBuild(cfg, path):
	return cfg['dir']['base'] + path

def awsSession(cfg):
	boto3.setup_default_session(profile_name=cfg['aws']['profile-user'])
	boto3.setup_default_session(region_name=cfg['aws']['aws-region'])

def composeStackDescribeCommand(cfg, fullOutputFile, stackName):
	return "aws cloudformation  describe-stacks " + \
		" --stack-name " + stackName + \
		" --profile " + cfg['aws']['profile-user'] + \
    	" --region " + cfg['aws']['aws-region'] + \
    	" > " + fullOutputFile

def runShell(command, commandName, commandDescription):
	print()
	print("------------------------------------ " + commandName + "  -->>  " + commandDescription)
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

def configOutputFileInitialize(cfg):
	cfgOutFile = pathFileBuild(cfg, cfg['dir']['output'], "config-output.json")
	if(cfg["aws"]["preserve-config-output-file"] != None and \
		cfg["aws"]["preserve-config-output-file"]  == False):
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

def getOutVal(cfgOutFile, stackName, outputKey):
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
			pSource["value"] = getOutVal(cfgOutFile, pSource["stackName"], pSource["outputKey"])
	return parametersSource

def ifExistRemoveFile(file):
	if os.path.isfile(file):
		print("Removing file at ... " + file)
		os.remove(file)

def ifExistRemoveDir(dir):
	if os.path.isdir(dir):
		print("Removing dir at ... " + dir)
		shutil.rmtree(dir)

def getDirs(cfg, st):
	retVal = {}
	retVal["stackFullName"] = cfg['project']['stack-base-name'] + "-" + st['name']	
	if(st["type"]=="Api"):
		retVal["stackFullName"] = cfg['project']['stack-base-name'] + "-api-" + st['name']
	retVal["fullFile"] = pathFileBuild(cfg, cfg['dir']['stacks'], st['name'] + ".yaml")
	retVal["outputDir"] = pathFileBuild(cfg, cfg['dir']['output'], st['name'] + ".yaml")
	retVal["apiDir"] = pathBuild(cfg, cfg['dir']['apis'])
	return retVal

def runPackage(cfg, st, cfgOutFile, outputDir, fullFile):
	deployFullFile = outputDir + "-deploy.yaml "
	bk = getOutVal(cfgOutFile, cfg['packages-deploy-bucket']["stackName"], \
		cfg['packages-deploy-bucket']["outputKey"])
	cmdPackage = " aws cloudformation package --template-file " + fullFile + \
		" --output-template-file " + outputDir + "-deploy.yaml" + \
		" --s3-bucket " + bk + " " \
		" --region " + cfg['aws']['aws-region'] + \
		" --profile " + cfg['aws']['profile-user']
	runShell(cmdPackage, st['name'], "package")
	return deployFullFile

def runDeploy(cfg, st, cfgOutFile, deployFullFile, stackFullName, swaggerFileName=""):
	cmd = " aws cloudformation deploy " + \
    		" --region " + cfg['aws']['aws-region'] + \
    		" --profile " + cfg['aws']['profile-user'] + \
    		" --template-file " + deployFullFile + \
    		" --stack-name " + stackFullName + \
    		" --capabilities CAPABILITY_IAM " + \
    		" --tags Project=" + cfg['project']['tag'] + \
    		" --parameter-overrides TagProject=" + cfg['project']['tag']
	if(st['parameters-source'] != None):
		for pS in st['parameters-source']:
			cmd = cmd + " " + pS["name"] + "=" + pS["value"]

	if(st['type']=="Api"):
		val = getOutVal(cfgOutFile, cfg['packages-deploy-bucket']["stackName"], \
		                                    cfg['packages-deploy-bucket']["outputKey"])
		val = "s3://" + val + "/" + swaggerFileName
		cmd = cmd + " " + cfg['packages-deploy-bucket']['swagger-file-param-name'] + "=" + val


	runShell(cmd, st['name'], "deploy")
	fullOutputFile = pathFileBuild(cfg, cfg['dir']['output'], stackFullName + "-output.json")
	runShell(composeStackDescribeCommand(cfg, fullOutputFile, stackFullName), st['name'], "decribe")
	extractOutputs(fullOutputFile, cfgOutFile, stackFullName, st['name'])

def copyArtifact(cfg, st, cfgOutFile, apiDir, swaggerFileName):
	bk = getOutVal(cfgOutFile, cfg['packages-deploy-bucket']["stackName"], \
		cfg['packages-deploy-bucket']["outputKey"]) + "/" + swaggerFileName
	cmd = " aws s3 cp " + apiDir + "\\" + st["name"] + "\\" + st["name"] + "-swagger.yaml" + " s3://" + \
	    bk + " --sse" + \
		" --region " + cfg['aws']['aws-region'] + \
		" --profile " + cfg['aws']['profile-user']
	runShell(cmd, st['name'], "sync artifacts ")

def idGenerator(size=32):
	chars = string.ascii_lowercase + string.digits
	return ''.join(random.choice(chars) for _ in range(size))

def runStack(cfg, st, cfgOutFile):
	v = getDirs(cfg, st)
	stackFullName = v["stackFullName"]
	fullFile = v["fullFile"]
	outputDir = v["outputDir"]
	apiDir = v["apiDir"]

	print()
	print()
	print("=======================================================================")
	print("Stack Name: " +  stackFullName)
	print("Stack Type: " + st["type"])
	print("Stack File: " +  st['name'] + ".yaml")
	
	ifExistRemoveFile(fullFile + "-deploy.yaml")
	
	if(st['parameters-source'] != None):
		setOutputValue(st['parameters-source'], cfgOutFile)
	
	swaggerFileName = st["name"] + "-swagger-"  + idGenerator()  + ".yaml"
	if(st["type"] == "Api"):
		copyArtifact(cfg, st, cfgOutFile, apiDir, swaggerFileName)

	deployFullFile = fullFile
	if(st["type"] == "Package"):
		deployFullFile = runPackage(cfg, st, cfgOutFile, outputDir, fullFile)
	if(st["type"] == "Api"):
		deployFullFile = runPackage(cfg, st, cfgOutFile, outputDir, \
			apiDir + "\\" + st['name'] + "\\" + st['name'] + ".yaml")

	runDeploy(cfg, st, cfgOutFile, deployFullFile, stackFullName, swaggerFileName)

def appBuildAndDeploy(cfg, cfgOutFile):
	appDir = pathBuild(cfg, cfg['dir']['app'])
	ifExistRemoveDir(appDir + "\\dist")

	print('------------------------------------ Build Distribution  -->  dir info')
	originalDir = os.path.dirname(os.path.realpath(__file__))
	print('Aws dir= ' + os.getcwd())
	os.chdir(appDir)
	print('App dir= ' + os.getcwd())

	cmd = " ng build --" + cfg['project']['env']
	runShell(cmd, 'Build Distribution', 'running ng build')
	
	distArtifacDir = pathFileBuild(cfg, cfg['dir']['output'], 'dist-artifacts')
	cmd = "mkdir " + distArtifacDir + " 2>nul"
	runShell(cmd, 'Build Distribution', 'create dir for artifact file')
	artifactFile = "dist_artifact" + time.strftime("%Y-%m-%d-%H-%M-%S") + ".zip"
	cmd = "7z a " + distArtifacDir + "\\" + artifactFile + " .\\dist"
	runShell(cmd, 'Build Distribution', 'zipping artifact with 7zip')

	# Upload artifact zip
	bk = getOutVal(cfgOutFile, cfg['packages-deploy-bucket']["stackName"], \
		cfg['packages-deploy-bucket']["outputKey"])
	cmd = " aws s3 cp " + distArtifacDir + "\\" + artifactFile + \
	      "  s3://" + bk + "  --acl private " + \
		" --region " + cfg['aws']['aws-region'] + \
		" --profile " + cfg['aws']['profile-user']
	runShell(cmd, 'Build Distribution', 'uploading artifact to s3')

	# Upload website
	bk = getOutVal(cfgOutFile, cfg['website-deploy-bucket']["stackName"], \
		cfg['website-deploy-bucket']["outputKey"])
	cmd = " aws s3 cp ./dist " + \
	      "  s3://" + bk + "  --acl public-read --recursive " + \
		" --region " + cfg['aws']['aws-region'] + \
		" --profile " + cfg['aws']['profile-user']
	runShell(cmd, 'Build Distribution', 'uploading dist to website bucket')

	print('------------------------------------ Build Distribution  -->  final dir info')
	os.chdir(originalDir)
	print('Aws dir= ' + os.getcwd())

def buildConfigFile(cfg, cOutFile):
	cfgDict = {}
	
	for k in cfg['config-values']:
		print(k)
		if('value' in k):
			cfgDict[k['name']] = k['value']
		elif('cfg-values'  in k):
			cfgDict[k['name']] = cfg[k['cfg-values']['level1']][k['cfg-values']['level2']]
		elif('stackName' in k):
			cfgDict[k['name']] = getOutVal(cOutFile, k['stackName'], k['outputKey'])

	data = "export const environment = " + json.dumps(cfgDict, separators=(',',':'), indent=2)
	envFile = pathFileBuild(cfg, cfg['dir']['app'] + "\\src\\environments" , "environments." + cfg['project']['env'] + ".ts")
	f = open(envFile, 'wt', encoding='utf-8')
	f.write(data)

def main():
	filePath = sys.argv[1]
	cfg = cfgLoad(filePath)
	awsSession(cfg)
	cfgOutFile = configOutputFileInitialize(cfg)
	
	for st in cfg['stacks']:
		if(st["skip"] != None and st["skip"] == False):
			runStack(cfg, st, cfgOutFile)

	buildConfigFile(cfg, cfgOutFile)

	if(cfg['project']['app-build-and-deploy']):
		appBuildAndDeploy(cfg, cfgOutFile)


	print("========================================================================")
	print("===========================      FINISH      ===========================")
	print("========================================================================")

if __name__ == '__main__':
	main()
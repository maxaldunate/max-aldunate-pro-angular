@echo off
set profile-user=testuser
set stack-name=max-aldunate-pro-cont-integration
set project-tags=max-pro
set aws-region=eu-west-1
set website-bucket-name=angularmax.aldunate.pro

@echo -
@echo Variables:
@echo profile user           = %profile-user%
@echo stack name             = %stack-name%
@echo project tags           = %project-tags%
@echo aws-region             = %aws-region%
@echo website-bucket-name    = %website-bucket-name%
@echo -
@echo cloudformation package ...
CALL aws cloudformation package ^
    --template-file aws-cont-integration.yaml ^
    --output-template-file aws-cont-integration-deploy.yaml ^
    --s3-bucket laguineu-deploy ^
    --profile %profile-user%
@echo -
@echo cloudformation deploy ...
CALL aws cloudformation deploy ^
     --region %aws-region% ^
     --template-file aws-cont-integration-deploy.yaml ^
     --stack-name %stack-name% ^
     --capabilities CAPABILITY_IAM ^
     --profile %profile-user% ^
     --tags Project=%project-tags% ^
     --parameter-overrides TagProject=%project-tags% ^
                           WebsiteBucketName=%website-bucket-name%
@echo -
@echo finished!

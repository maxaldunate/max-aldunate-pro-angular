@echo off
set profile-user=testuser
set stack-name=max-aldunate-pro-cognito
set project-tags=max-pro
set aws-region=eu-west-1
@echo -
@echo Variables:
@echo profile user  = %profile-user%
@echo stack name    = %stack-name%
@echo project tags  = %project-tags%
@echo aws-region    = %aws-region%
@echo -
@echo cloudformation package ...
CALL aws cloudformation package ^
    --template-file aws-congnito.yaml ^
    --output-template-file aws-congnito-deploy.yaml ^
    --s3-bucket laguineu-deploy ^
    --profile %profile-user%
@echo -
@echo cloudformation deploy ...
CALL aws cloudformation deploy ^
     --region %aws-region% ^
     --template-file aws-congnito-deploy.yaml ^
     --stack-name %stack-name% ^
     --capabilities CAPABILITY_IAM ^
     --profile %profile-user% ^
     --tags Project=%project-tags% ^
     --parameter-overrides TagProject=%project-tags%
@echo -
@echo finished!

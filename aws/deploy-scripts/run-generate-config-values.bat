@echo off
set profile-user=testuser
set aws-region=eu-west-1
set stack-cognito=max-aldunate-pro-cognito
set stack-cont-integration=max-aldunate-pro-cont-integration
set stack-api=max-aldunate-pro-api
@echo -
@echo Variables:
@echo profile user  = %profile-user%
@echo aws-region    = %aws-region%
@echo stack-cognito=%stack-cognito%
@echo stack-cont-integration=%stack-cont-integration%
@echo stack-api=%stack-api%

@echo -
CALL aws cloudformation ^
         --profile %profile-user% --region %aws-region% ^
         describe-stacks --stack-name %stack-cognito% ^
         > %stack-cognito%-config-value.json

@echo -
CALL aws cloudformation ^
         --profile %profile-user% --region %aws-region% ^
         describe-stacks --stack-name %stack-cognito% ^
         > %stack-cognito%-config-value.json

@echo -
CALL aws cloudformation ^
         --profile %profile-user% --region %aws-region% ^
         describe-stacks --stack-name %stack-cont-integration% ^
         > %stack-cont-integration%-config-value.json

@echo -
CALL aws cloudformation ^
         --profile %profile-user% --region %aws-region% ^
         describe-stacks --stack-name %stack-api% ^
         > %stack-api%-config-value.json

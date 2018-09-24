@echo off
REM References
REM https://github.com/aws-samples/aws-serverless-ember
REM https://aws.amazon.com/blogs/developer/creating-and-deploying-a-serverless-web-application-with-cloudformation-and-ember-js/
REM https://aws.amazon.com/getting-started/serverless-web-app/module-3/

REM aws cloudformation deploy --template-file hosting.yaml --stack-name ember-serverless-hosting --capabilities CAPABILITY_IAM --profile testuser
REM aws cloudformation describe-stacks --stack-name ember-serverless-hosting

REM CALL aws cloudformation package      --template-file api.yaml      --output-template-file api-deploy.yaml      --s3-bucket ember-serverless-hosting-codebucket-1vvd9vfac4rrb  --profile testuser 
REM aws cloudformation describe-stacks --stack-name ember-serverless-api

REM CALL aws cloudformation deploy --template-file api-deploy.yaml --stack-name ember-serverless-api --capabilities CAPABILITY_IAM    --profile testuser --region eu-west-1

REM cd ..\client\vendor
REM aws apigateway get-sdk --rest-api-id l1ew2v0lnd --stage-name Prod --sdk-type javascript ./apiGateway-js-sdk.zip --profile testuser

REM unzip on vendor
REM modify envorinment.js
REM aws cloudformation describe-stacks --stack-name ember-serverless-api

REM ENV.AWS_POOL_ID -> CognitoIdentityPoolId
REM ENV.AWS_USER_POOL_ID -> CognitoUserPoolsId
REM ENV.AWS_CLIENT_ID -> CognitoUserPoolsClientId

REM cd client
REM ember build
REM aws s3 sync dist/ s3://ember-serverless-hosting-websitebucket-12uowt9u3x9wd/ --acl public-read  --profile testuser

REM templates/aws-congnito-components-for-identification-server.yaml
REM templates/serverless-static-client-hosting.yaml


@echo off
set profile-user=testuser
set stack-name=laguineu-identity
set project-tags=laguineu
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
    --template-file templates/aws-congnito-components-for-identification-server.yaml ^
    --output-template-file templates/aws-congnito-components-for-identification-server.yaml-deploy.yaml ^
    --s3-bucket laguineu-deploy ^
    --profile %profile-user%
@echo -
@echo cloudformation deploy ...
CALL aws cloudformation deploy ^
     --region %aws-region% ^
     --template-file templates/aws-congnito-components-for-identification-server.yaml-deploy.yaml ^
     --stack-name %stack-name% ^
     --capabilities CAPABILITY_IAM ^
     --profile %profile-user% ^
     --tags Project=%project-tags% ^
     --parameter-overrides TagProject=%project-tags%
@echo -
@echo finished!

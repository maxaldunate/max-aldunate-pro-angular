@echo off
set profile-user=testuser
set stack-name=max-aldunate-pro-api
set project-tags=max-pro
set aws-region=eu-west-1
set template-file-name=course-api
set bucket-templates=angularmax.aldunate.pro-artifacts
set swagger-file-name=course-swagger.yaml

@echo -
@echo Variables:
@echo profile user          = %profile-user%
@echo stack name            = %stack-name%
@echo project tags          = %project-tags%
@echo aws-region            = %aws-region%
@echo template-file-name    = %template-file-name%
@echo bucket-templates      = %bucket-templates%
@echo swagger-file-name     = %swagger-file-name%

echo -
echo copy swagger file ...

CALL aws s3 cp ^
        %swagger-file-name% ^
        s3://%bucket-templates%/%swagger-file-name% ^
        --sse ^
        --profile %profile-user%

@echo -
@echo cloudformation package ...

CALL aws cloudformation package ^
         --template-file %template-file-name%.yaml ^
         --output-template-file %template-file-name%-deploy.yaml ^
         --profile %profile-user% ^
         --s3-bucket=%bucket-templates%
    
echo -
echo cloudformation deploy ...

CALL aws cloudformation deploy ^
      --region %aws-region% ^
      --template-file %template-file-name%-deploy.yaml ^
      --stack-name %stack-name% ^
      --capabilities CAPABILITY_IAM ^
      --profile %profile-user% ^
      --tags Project=%project-tags% ^
      --parameter-overrides TagProject=%project-tags% SwaggerS3File=s3://%bucket-templates%/%swagger-file-name%

@echo -
@echo finished!

@echo off
set profile-user=testuser
set aws-region=eu-west-1

@echo -
@echo Variables:
@echo profile user  = %profile-user%
@echo aws-region    = %aws-region%

@echo validating ...
CALL aws cloudformation validate-template ^
         --template-body file://templates/aws-congnito-components-for-identification-server.yaml ^
         --profile %profile-user% ^
         --region %aws-region%
@echo -
@echo finished!

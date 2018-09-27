@echo off
@echo validating ...
CALL aws cloudformation validate-template --template-body ^
               file://course-api.yaml ^
               --profile testuser ^
               --region eu-west-1
@echo -
@echo finished!

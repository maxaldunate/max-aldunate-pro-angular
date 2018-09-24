@echo off
set profile-user=testuser
set project-tags=max-pro
set aws-region=eu-west-1
set website-bucket-name=angularmax.aldunate.pro
set artifact-bucket-name=angularmax.aldunate.pro-artifacts
set artifact-file=dist_artifact_%date:~-4,4%_%date:~-7,2%_%date:~-10,2%_%time:~0,2%_%time:~3,2%_%time:~6,2%.zip

@echo -
@echo Variables:
@echo profile user           = %profile-user%
@echo project tags           = %project-tags%
@echo aws-region             = %aws-region%
@echo website-bucket-name    = %website-bucket-name%
@echo artifact-file          = %artifact-file%
@echo -

@echo ================ moving to app dir =====================================
CALL cd ..\..\app

@echo ================ remove dist folder ====================================
CALL rmdir .\dist /s/q

@echo ================ build distribution ====================================
CALL ng build --dev

@echo ================ generating zip artifact ===============================
mkdir dist-artifacts 2>nul
7z a dist-artifacts\%artifact-file% .\dist

@echo ================ copying artifact to bucket ============================
CALL aws s3 cp ^
            %artifact-file% ^
            s3://%artifact-bucket-name%/ ^
            --profile %profile-user%  ^
            --acl private

@echo ================ deploying artifact to bucket website ==================
CALL aws s3 cp ./dist s3://%website-bucket-name%/ ^
               --profile %profile-user% --recursive --acl public-read

@echo ================ comming back to con-integration folder ================
CALL cd ..\aws\cont-integration
@echo -
@echo finished!
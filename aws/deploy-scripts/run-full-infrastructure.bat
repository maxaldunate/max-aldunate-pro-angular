@echo off
set base-dir="D:\cloud\github\current\adolfo\max-aldunate-pro-angular"
@echo -
@echo Variables:
@echo base-dir  = %base-dir%

@echo ********************************************************************
@echo ================ Stack Cognito =====================================
@echo ********************************************************************
CALL %base-dir%/aws/stack/cognito/run.bat

@echo ********************************************************************
@echo ================ Stack Continuous Integration ======================
@echo ********************************************************************
CALL %base-dir%/aws/stack/cont-integration/run.bat

@echo ********************************************************************
@echo ================ Build and Deploy API ==============================
@echo ********************************************************************

CALL %base-dir%/api/src/course/run.bat


CALL 


Falta Generar fichero de configuracion


@echo ********************************************************************
@echo ================ Build and Deploy APP ==============================
@echo ********************************************************************
CALL ./aws/cont-integration/build-and-deply-app.bat


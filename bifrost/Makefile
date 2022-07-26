# ==============================================================================
# DATOS DEL PROYECTO
# ==============================================================================
PROJECT = bifrost
LAYER_NAME = bifrost
DESCRIPTION = "Librerías combinadas de bifrost en un solo layer"

DEV_AWS_REGION = sa-east-1
RELEASE_AWS_REGION = us-east-1
PROD_AWS_REGION = us-west-2

# ==============================================================================
# CONFIGURACIONES ESTATICAS
# ==============================================================================
VIRTUAL_ENV = env
REQUIREMENTS = setup/requirements
RUNTIME_VERSION = 3.8
LAYER_VERSION = 1
LAYER_BUILD_DIR = ./package/tmp/python

# ==============================================================================
# CONFIGURACIONES DE COLORES
# ==============================================================================
HEADER = '\033[96m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
END = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

ifdef PROFILE
	ORGANIZATION_ID = $(shell aws sts get-caller-identity --profile $(PROFILE)| jq -r '.["Account"]';)
else
	PROFILE = default
	ORGANIZATION_ID = $(shell aws sts get-caller-identity | jq -r '.["Account"]';)
endif

# ==============================================================================
# DEFAULT COMMANDS
# ==============================================================================
install: virtual install_requirements
build: install clean_package build_package_tmp copy_python remove_unused zip

deploy: dev_set install build s3_upload layer_create
deploy_test: dev_set install build s3_upload layer_create_test

deploy_release: release_set install build s3_upload layer_create
deploy_test_release: release_set install build s3_upload layer_create_test
delete_release: release_set layer_delete

deploy_prod: prod_set install build s3_upload layer_create
deploy_test_prod: prod_set install build s3_upload layer_create_test
delete_prod: prod_set layer_delete

build_docker: clean_package build_package_tmp install_requirements_docker zip
deploy_docker: build_docker s3_upload layer_create

clean: clean_package
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(HEADER)"Limpando Archivos compilados"$(END)
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@rm -rf ./$(FUNCTION_NAME)/*.pyc
	@+echo $(OKGREEN)"[OK] Archivos compilados eliminados."$(END)
	@+echo ""

prod_set:
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(HEADER)"Carga Productiva"$(END)
	@+echo $(HEADER)"---------------------------------------------"$(END)
	$(eval AWS_REGION=$(PROD_AWS_REGION))
	$(eval STAGE=prod)

release_set:
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(HEADER)"Carga Release"$(END)
	@+echo $(HEADER)"---------------------------------------------"$(END)
	$(eval AWS_REGION=$(RELEASE_AWS_REGION))
	$(eval STAGE=release)

dev_set:
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(HEADER)"Carga Desarrollo"$(END)
	@+echo $(HEADER)"---------------------------------------------"$(END)
	$(eval AWS_REGION=$(DEV_AWS_REGION))
	$(eval STAGE=dev)

uninstall: clean
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(HEADER)"Desinstalando paquetes y entorno virtual"$(END)
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@rm -rf ./$(VIRTUAL_ENV)
	@+echo $(OKGREEN)"[OK] Entorno virtual desinstalado"$(END)
	@rm -rf ./package
	@+echo $(OKGREEN)"[OK] Paquetes desinstalado"$(END)
	@+echo ""

virtual:
	@+echo "---------------------------------------------"$(END)
	@+echo  $(HEADER)"Instalando y activando entorno virtual"
	@+echo "---------------------------------------------"$(END)
	@+echo $(WARNING)""
	@if test ! -d "$(VIRTUAL_ENV)"; then \
		python$(RUNTIME_VERSION) -m venv $(VIRTUAL_ENV); \
	fi
	@+echo ""$(END)

install_requirements:
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(HEADER)"Instalando paquetes requeridos por el entorno"$(END)
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(WARNING)""
	@ $(VIRTUAL_ENV)/bin/pip --no-cache-dir install -Ur $(REQUIREMENTS)
	@ touch $(VIRTUAL_ENV)/bin/activate
	@+echo $(OKGREEN)"[OK] Paquetes instalados"$(END)
	@+echo ""

install_requirements_docker:
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(HEADER)"Instalando paquetes requeridos por el entorno"$(END)
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(WARNING)""
	@docker run --rm -v `pwd`:/foo -w /foo lambci/lambda:build-python$(RUNTIME_VERSION) python$(RUNTIME_VERSION) -m pip --isolated install -r $(REQUIREMENTS) --no-deps -t ${LAYER_BUILD_DIR}
	@+echo $(OKGREEN)"[OK] Paquetes instalados"$(END)
	@+echo ""

clean_package:
	@rm -rf ./package/*

build_package_tmp:
	@+echo $(HEADER)"============================================="$(END)
	@+echo $(HEADER)"CONSTRUYENDO PACKAGE '"$(LAYER_NAME)"'" $(END)
	@+echo $(HEADER)"============================================="$(END)
	@mkdir -p ${LAYER_BUILD_DIR}
	@cp -a ./$(PROJECT)/. ${LAYER_BUILD_DIR}

copy_python:
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(HEADER)"Cargando librerias"$(END)
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@if test -d $(VIRTUAL_ENV)/lib; then \
		cp -a $(VIRTUAL_ENV)/lib/python$(RUNTIME_VERSION)/site-packages/. ${LAYER_BUILD_DIR}; \
	fi
	@if test -d $(VIRTUAL_ENV)/lib64; then \
		cp -a $(VIRTUAL_ENV)/lib64/python$(RUNTIME_VERSION)/site-packages/. ${LAYER_BUILD_DIR}; \
	fi
	@+echo $(OKGREEN)"[OK] Librerias cargadas"$(END)
	@+echo ""

remove_unused:
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(HEADER)"Eliminando archivos sin uso"$(END)
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@rm -rf ${LAYER_BUILD_DIR}/wheel*
	@rm -rf ${LAYER_BUILD_DIR}/easy-install*
	@rm -rf ${LAYER_BUILD_DIR}/setuptools*
	@rm -rf ${LAYER_BUILD_DIR}/pip*
	@rm -rf ${LAYER_BUILD_DIR}/pkg_resources*
	@rm -rf ${LAYER_BUILD_DIR}/__pycache__
	@rm -rf env/
	@+echo $(OKGREEN)"[OK] Archivos eliminados"$(END)
	@+echo ""

zip:
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(HEADER)"Empaquetando"$(END)
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@if ! cd ./package/tmp && zip -q -r ../$(PROJECT).zip .; then \
		echo $(FAIL)"[ERROR] Problema en el empaquetamiento."$(END); \
	else \
		zip -q -r ../$(PROJECT).zip . ; \
		echo $(OKGREEN)"[OK] Empaquetado finalizado"$(END); \
	fi
	@+echo ""

# ==============================================================================
# LAYER COMMANDS
# ==============================================================================
layer_delete:
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(HEADER)"Eliminando capa de AWS Lambda"$(END)
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@if ! aws lambda delete-layer-version \
		--region $(AWS_REGION) \
		--version-number $(LAYER_VERSION) \
		--layer-name $(LAYER_NAME) \
		--profile $(PROFILE); then \
		echo $(FAIL)"[ERROR] No se pudo eliminar la capa de AWS Lambda, puede que la capa no exista"$(END);\
	else \
		echo $(OKGREEN)"[OK] Eliminación Completada"$(END); \
	fi
	@+echo ""

layer_create:
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(HEADER)"Creando capa en AWS Lambda"$(END)
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@if ! aws lambda publish-layer-version \
		--region $(AWS_REGION) \
		--layer-name $(LAYER_NAME) \
		--description $(DESCRIPTION) \
		--content S3Bucket=$(ORGANIZATION_ID)-lambda-layers-$(AWS_REGION),S3Key=$(LAYER_NAME).zip \
		--compatible-runtimes python$(RUNTIME_VERSION) \
		--profile $(PROFILE); then \
		echo $(FAIL)"[ERROR] Despliegue fallido"$(END);\
	else \
		echo $(OKGREEN)"[OK] Despliegue finalizado"$(END); \
	fi

layer_create_test:
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(HEADER)"Creando capa de prueba en AWS Lambda"$(END)
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@if ! aws lambda publish-layer-version \
		--region $(AWS_REGION) \
		--layer-name $(LAYER_NAME)_test \
		--description $(DESCRIPTION) \
		--content S3Bucket=$(ORGANIZATION_ID)-lambda-layers-$(AWS_REGION),S3Key=$(LAYER_NAME).zip \
		--compatible-runtimes python$(RUNTIME_VERSION) \
		--profile $(PROFILE); then \
		echo $(FAIL)"[ERROR] Despliegue fallido"$(END);\
	else \
		echo $(OKGREEN)"[OK] Despliegue finalizado"$(END); \
	fi

# ==============================================================================
# SAM COMMANDS
# ==============================================================================
sam_build:
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(HEADER)"Construyendo package" $(END)
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(BOLD)""
	@if ! sam build \
		--build-dir $(SAM_PACKAGE_PATH) \
		--use-container \
		--manifest $(REQUIREMENTS) \
		--template $(SAM_TEMPLATE) \
		--region $(AWS_REGION) \
		--profile $(PROFILE); then \
		echo $(FAIL)"[ERROR] Error en la construcción del package."$(END); \
	else \
		echo $(OKGREEN)"[OK] Package local construido."$(END); \
	fi
	@if mv ${SAM_PACKAGE_PATH}${SAM_NAME_FUNCTION}/* ${SAM_PACKAGE_PATH}.; then \
		echo $(OKGREEN)"[OK] Librerías cargadas en package."$(END); \
	else \
		echo $(WARNING)"[WARNING] Librerías no encontradas o no se pudieron mover al package."$(END); \
	fi
	@+rm -rf ${SAM_PACKAGE_PATH}${SAM_NAME_FUNCTION};
	@+echo ""

# ==============================================================================
# S3 COMMANDS
# ==============================================================================
s3_upload:
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@+echo $(HEADER)"Subiendo función a bucket S3"$(END)
	@+echo $(HEADER)"---------------------------------------------"$(END)
	@if ! aws s3 cp \
		./package/$(PROJECT).zip \
		s3://$(ORGANIZATION_ID)-lambda-layers-$(AWS_REGION)/$(PROJECT).zip \
		--region $(AWS_REGION) \
		--profile $(PROFILE); then \
		echo $(FAIL)"[ERROR] Subida fallida"$(END);\
	else \
		echo $(OKGREEN)"[OK] Subida finalizada"$(END); \
	fi

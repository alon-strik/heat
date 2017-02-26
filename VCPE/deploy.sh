#!/bin/bash

echo "--- Start deploying ---"

#cfy uninstall -d vCpe
cfy blueprints delete -b Fortigate
cfy blueprints delete -b Vyatta
cfy blueprints delete -b vCPE

cfy blueprints upload -p ./Fortigate.yaml -b Fortigate
cfy blueprints upload -p ./Vyatta.yaml   -b Vyatta
cfy install -d vCPE -p ./vCPE-blueprint.yaml

cfy executions list | grep vCPE

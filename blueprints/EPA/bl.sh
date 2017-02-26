cfy blueprints upload -b router$1 -p mwc-demo-blueprint.yaml
sleep 2
cfy deployments create -b router$1 -d routert$1 -i mwc-demo-blueprint-input.yaml

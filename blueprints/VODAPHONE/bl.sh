cfy blueprints upload -b fortinet$1 -p fortinet-blueprint.yaml
sleep 5
cfy deployments create -b fortinet$1 -d fortinet$1 -i fortinet-blueprint-input.yaml

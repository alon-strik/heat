cfy blueprints upload -b test$1 -p fortinet-blueprint-test.yaml
sleep 5
cfy deployments create -b test$1 -d test$1 -i fortinet-blueprint-input-test.yaml

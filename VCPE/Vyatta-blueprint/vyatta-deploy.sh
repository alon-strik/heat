#!/usr/bin/env bash

cfy blueprints upload -b vyatta$1 -p vyatta-blueprint.yaml
sleep 5
cfy deployments create -b vyatta$1 -d vyatta$1 -i vyatta-blueprint-input.yaml

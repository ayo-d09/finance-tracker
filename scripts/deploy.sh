#!/bin/bash
set -e

terraform -chdir=infra init
terraform -chdir=infra plan
terraform -chdir=infra apply


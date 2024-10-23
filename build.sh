#!/bin/bash
docker build -t localhost:5000/mobiflow-auditor:0.0.1 .
docker push localhost:5000/mobiflow-auditor:0.0.1

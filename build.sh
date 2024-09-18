#!/bin/bash
docker build -t localhost:5000/mobiflow-auditor:0.0.3 .
docker push localhost:5000/mobiflow-auditor:0.0.3
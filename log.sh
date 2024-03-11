#!/bin/bash
sudo kubectl logs $(sudo kubectl get pods -o name -n ricxapp | grep "mobiflow-auditor") -n ricxapp -f

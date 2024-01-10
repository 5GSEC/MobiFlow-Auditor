<!--
SPDX-FileCopyrightText: Copyright 2004-present Facebook. All Rights Reserved.
SPDX-FileCopyrightText: 2019-present Open Networking Foundation <info@opennetworking.org>

SPDX-License-Identifier: Apache-2.0
-->
# MobiFlow-Auditor
MobiFlow Auditor xApp

This app subscribes to the kpm (key performance metrics) service model and exposes
the metrics via a prometheus gauge endpoint.

## Deploy container

You can deploy the `mobiflow-auditor` image using helm:
```
./install_secsm_xapp.sh
```

uninstall:
```
./uninstall_secsm_xapp.sh
```

view logs:
```
kubectl logs --namespace=riab --tail=100 -lname=mobiflow-auditor -f
```

# SPDX-FileCopyrightText: Copyright 2004-present Facebook. All Rights Reserved.
# SPDX-FileCopyrightText: 2019-present Open Networking Foundation <info@opennetworking.org>
#
# SPDX-License-Identifier: Apache-2.0

FROM python:3.8-slim

# install all deps
WORKDIR /usr/local

RUN pip install grpcio grpcio-tools

COPY onos_e2_sm ./onos_e2_sm
RUN pip install --upgrade pip ./onos_e2_sm --no-cache-dir

# speed up subsequent image builds by pre-dl and pre-installing pre-reqs
COPY mobiflow-auditor/setup.py ./secsm/setup.py
RUN pip install ./secsm --no-cache-dir

# install actual app code
COPY mobiflow-auditor ./secsm
RUN pip install ./secsm --no-cache-dir

ENTRYPOINT [ "python" ]

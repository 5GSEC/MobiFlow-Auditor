#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright 2004-present Facebook. All Rights Reserved.
# SPDX-FileCopyrightText: 2019-present Open Networking Foundation <info@opennetworking.org>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Iterator, List

from prometheus_client.core import GaugeMetricFamily, Metric, REGISTRY


class CustomCollector:
    def __init__(self) -> None:
        self.metrics = {}

    def register(self, measurement_id: int, measurement_name: str,) -> None:
        if measurement_id in self.metrics or measurement_name in self.metrics:
            return

        metric_name = "fb_xappkpimon_" + measurement_name.lower().replace(".", "_")
        metric = GaugeMetricFamily(
            metric_name,
            measurement_name,  # description
            labels=["nodeid", "cellid"],
        )

        self.metrics[measurement_id] = metric
        self.metrics[measurement_name] = metric

    def collect(self) -> Iterator[Metric]:
        for metric_family in self.metrics.values():
            yield metric_family
            metric_family.samples.clear()


CUSTOM_COLLECTOR = CustomCollector()
REGISTRY.register(CUSTOM_COLLECTOR)

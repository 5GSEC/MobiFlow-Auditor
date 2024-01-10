#!/usr/bin/env python3
# Copyright 2004-present Facebook. All Rights Reserved.
# SPDX-FileCopyrightText: 2019-present Open Networking Foundation <info@opennetworking.org>
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import asyncio
import pathlib
import json
from typing import Any, Dict

from secsm.onos_ric_secsm import *
import onos_ric_sdk_py as sdk

async def async_main(
    app_config: Dict[str, Any],
    e2_client: sdk.E2Client,
    sdl_client: sdk.SDLClient,
) -> None:
    async with e2_client, sdl_client:
        async for e2_node_id, e2_node in sdl_client.watch_e2_connections():
            try:
                service_model = next(
                    sm
                    for oid, sm in e2_node.service_models.items()
                    if oid == KPM_SERVICE_MODEL_OID_V2
                )
            except StopIteration:
                continue

            asyncio.create_task(
                run(
                    app_config,
                    e2_client,
                    sdl_client,
                    e2_node_id,
                    e2_node,
                    service_model,
                )
            )


def main(args: argparse.Namespace) -> None:
    config = json.loads(pathlib.Path(args.ric_config).read_text())
    e2_client = sdk.E2Client(**config["e2_client"])
    sdl_client = sdk.SDLClient(**config["sdl_client"])

    with open(args.path) as f:
        app_config = json.load(f)
        init_global(app_config)
        sdk.run(async_main(app_config, e2_client, sdl_client), args.path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="secsm xApp.")
    parser.add_argument(
        "--path", type=str, help="path to the service's JSON configuration file"
    )
    parser.add_argument(
        "--ric-config",
        type=str,
        help="ric module config",
        default="/etc/fb/config/onos.json",
    )
    args = parser.parse_args()
    main(args)



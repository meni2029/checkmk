#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Iterable, Mapping

import pytest

from cmk.agent_based.v1.type_defs import StringByteTable
from cmk.plugins.collection.agent_based.if_brocade_lancom import (
    parse_if_brocade_lancom,
    parse_if_lancom,
)


@pytest.mark.parametrize(
    "if_table,name_map,port_map,ignore,expected_results",
    [
        (
            [
                [
                    "1",
                    "eth0",
                    "2",
                    "30",
                    "1",
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "10",
                    "11",
                    "12",
                    "13",
                    "eth0",
                    [0, 12, 206, 149, 55, 128],
                    "Local0",
                ],
                [
                    "1",
                    "eth0",
                    "2",
                    "30",
                    "1",
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "10",
                    "11",
                    "12",
                    "13",
                    "eth1",
                    [0, 12, 206, 149, 55, 128],
                    "Logical Network",
                ],
            ],
            {"eth0": "LAN"},
            {},
            {"Local"},
            (("1", "eth0 Logical LAN", "eth1", "2", 30000000),),
        ),
    ],
)
def test_parse_if_brocade_lancom(
    if_table: StringByteTable,
    name_map: Mapping[str, str],
    port_map: Mapping[str, str],
    ignore: Iterable[str],
    expected_results: object,
) -> None:
    results = tuple(
        (r.index, r.descr, r.alias, r.type, r.speed)
        for r in (
            iface.attributes
            for iface in parse_if_brocade_lancom(if_table, name_map, port_map, ignore)
        )
    )
    assert results == expected_results


@pytest.mark.parametrize(
    "string_table, expected_results",
    [
        (
            [
                [
                    [
                        "1",
                        "ETH-1",
                        "6",
                        "1000",
                        "1",
                        "509221781931",
                        "496980435",
                        "92814480",
                        "115256031",
                        "0",
                        "0",
                        "454804812015",
                        "529803796",
                        "320739",
                        "481389",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 160, 87, 64, 128, 3],
                        "Switch Port ETH-1",
                    ],
                    [
                        "2",
                        "ETH-2",
                        "6",
                        "0",
                        "7",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 160, 87, 64, 128, 3],
                        "Switch Port ETH-2",
                    ],
                    [
                        "3",
                        "ETH-3",
                        "6",
                        "1000",
                        "1",
                        "57526111470",
                        "232373727",
                        "323364",
                        "23348",
                        "0",
                        "0",
                        "75485937857",
                        "108402742",
                        "258677",
                        "30904",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 160, 87, 64, 128, 3],
                        "Switch Port ETH-3",
                    ],
                    [
                        "4",
                        "ETH-4",
                        "6",
                        "1000",
                        "1",
                        "476089",
                        "1972",
                        "0",
                        "640",
                        "0",
                        "0",
                        "113216609",
                        "1283",
                        "258699",
                        "13594",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 160, 87, 64, 128, 3],
                        "Switch Port ETH-4",
                    ],
                    [
                        "5",
                        "WAN-1",
                        "6",
                        "1000",
                        "1",
                        "90039023655",
                        "338923579",
                        "0",
                        "232",
                        "0",
                        "0",
                        "707612504200",
                        "588826593",
                        "323375",
                        "53992",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 160, 87, 64, 128, 3],
                        "Switch Port WAN-1",
                    ],
                    [
                        "6",
                        "WAN-2",
                        "6",
                        "1000",
                        "1",
                        "10369425",
                        "42195",
                        "0",
                        "10058",
                        "0",
                        "0",
                        "119419561",
                        "46872",
                        "258509",
                        "4173",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 160, 87, 64, 128, 3],
                        "Switch Port WAN-2",
                    ],
                    [
                        "7",
                        "LAN-1",
                        "6",
                        "1000",
                        "1",
                        "506379537226",
                        "496975997",
                        "91542938",
                        "114009960",
                        "69858290",
                        "0",
                        "452406838224",
                        "529853749",
                        "320749",
                        "593383",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 160, 87, 64, 128, 3],
                        "AR8327",
                    ],
                    [
                        "8",
                        "LAN-2",
                        "6",
                        "0",
                        "7",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 160, 87, 64, 128, 3],
                        "AR8327",
                    ],
                    [
                        "9",
                        "LAN-3",
                        "6",
                        "1000",
                        "1",
                        "56569067135",
                        "232314806",
                        "323362",
                        "23335",
                        "128487",
                        "0",
                        "75049517526",
                        "108402846",
                        "258677",
                        "30909",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 160, 87, 64, 128, 3],
                        "AR8327",
                    ],
                    [
                        "10",
                        "LAN-4",
                        "6",
                        "1000",
                        "1",
                        "463716",
                        "1969",
                        "0",
                        "637",
                        "21",
                        "0",
                        "112067777",
                        "1285",
                        "258702",
                        "13596",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 160, 87, 64, 128, 3],
                        "AR8327",
                    ],
                    [
                        "11",
                        "LAN-5",
                        "6",
                        "1000",
                        "1",
                        "88699617602",
                        "339025976",
                        "0",
                        "228",
                        "295226",
                        "0",
                        "705250222045",
                        "588829407",
                        "323381",
                        "54009",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 160, 87, 64, 128, 3],
                        "AR8327",
                    ],
                    [
                        "12",
                        "LAN-6",
                        "6",
                        "1000",
                        "1",
                        "10160413",
                        "42195",
                        "0",
                        "10058",
                        "5",
                        "0",
                        "117954000",
                        "46872",
                        "258511",
                        "4174",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 160, 87, 64, 128, 3],
                        "AR8327",
                    ],
                    [
                        "94",
                        "DSL-1",
                        "6",
                        "0",
                        "2",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 160, 87, 64, 128, 3],
                        "AR8327",
                    ],
                    [
                        "95",
                        "DSL-CH-1",
                        "70",
                        "0",
                        "2",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 0, 0, 0, 0, 0],
                        "DSL-Channel #0",
                    ],
                    [
                        "96",
                        "DSL-CH-2",
                        "70",
                        "0",
                        "2",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 0, 0, 0, 0, 0],
                        "DSL-Channel #1",
                    ],
                    [
                        "97",
                        "DSL-CH-3",
                        "70",
                        "0",
                        "2",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 0, 0, 0, 0, 0],
                        "DSL-Channel #2",
                    ],
                    [
                        "98",
                        "DSL-CH-4",
                        "70",
                        "0",
                        "2",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 0, 0, 0, 0, 0],
                        "DSL-Channel #3",
                    ],
                    [
                        "99",
                        "DSL-CH-5",
                        "70",
                        "0",
                        "2",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 0, 0, 0, 0, 0],
                        "DSL-Channel #4",
                    ],
                    [
                        "100",
                        "DSL-CH-6",
                        "70",
                        "0",
                        "2",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 0, 0, 0, 0, 0],
                        "DSL-Channel #5",
                    ],
                    [
                        "101",
                        "DSL-CH-7",
                        "70",
                        "0",
                        "2",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 0, 0, 0, 0, 0],
                        "DSL-Channel #6",
                    ],
                    [
                        "102",
                        "DSL-CH-8",
                        "70",
                        "0",
                        "2",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "0",
                        "",
                        [0, 0, 0, 0, 0, 0],
                        "DSL-Channel #7",
                    ],
                ],
                [],
                [
                    ["2", "0"],
                    ["3", "512"],
                    ["4", "2"],
                    ["5", "0"],
                    ["17", "4"],
                    ["18", "5"],
                ],
            ],
            (
                ("1", "ETH-1", "maps to LAN-1", "6", 1000000000),
                ("2", "ETH-2", "maps to DSL-1", "6", 0),
                ("3", "ETH-3", "maps to LAN-3", "6", 1000000000),
                ("4", "ETH-4", "maps to LAN-1", "6", 1000000000),
                ("5", "WAN-1", "maps to LAN-5", "6", 1000000000),
                ("6", "WAN-2", "maps to LAN-6", "6", 1000000000),
                ("7", "LAN-1", "belongs to ETH-1 and ETH-4", "6", 1000000000),
                ("8", "LAN-2", None, "6", 0),
                ("9", "LAN-3", "belongs to ETH-3", "6", 1000000000),
                ("10", "LAN-4", None, "6", 1000000000),
                ("11", "LAN-5", "belongs to WAN-1", "6", 1000000000),
                ("12", "LAN-6", "belongs to WAN-2", "6", 1000000000),
                ("94", "DSL-1", "belongs to ETH-2", "6", 0),
                ("95", "DSL-CH-1", None, "70", 0),
                ("96", "DSL-CH-2", None, "70", 0),
                ("97", "DSL-CH-3", None, "70", 0),
                ("98", "DSL-CH-4", None, "70", 0),
                ("99", "DSL-CH-5", None, "70", 0),
                ("100", "DSL-CH-6", None, "70", 0),
                ("101", "DSL-CH-7", None, "70", 0),
                ("102", "DSL-CH-8", None, "70", 0),
            ),
        ),
    ],
)
def test_parse_if_lancom(string_table: list[StringByteTable], expected_results: object) -> None:
    results = tuple(
        (r.index, r.descr, r.extra_info, r.type, r.speed)
        for r in (iface.attributes for iface in parse_if_lancom(string_table))
    )
    assert results == expected_results


if __name__ == "__main__":
    # Please keep these lines - they make TDD easy and have no effect on normal test runs.
    # Just run this file from your IDE and dive into the code.
    import os

    from tests.testlib.common.repo import repo_path

    assert not pytest.main(
        [
            "--doctest-modules",
            os.path.join(repo_path(), "cmk/plugins.collection.agent_based/if_brocade_lancom.py"),
        ]
    )
    pytest.main(["-vvsx", __file__])

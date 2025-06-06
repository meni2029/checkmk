#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import pytest

from cmk.agent_based.v2 import CheckResult, Metric, Result, State, StringTable
from cmk.plugins.aws.lib import (
    aws_region_to_monitor,
    AWSLimits,
    check_aws_limits,
    check_aws_limits_legacy,
    CloudwatchInsightsSection,
    extract_aws_metrics_by_labels,
    GenericAWSSection,
    LambdaFunctionConfiguration,
    LambdaInsightMetrics,
    LambdaSummarySection,
    parse_aws,
    parse_aws_limits_generic,
)


@pytest.mark.parametrize(
    "string_table, expected_result",
    [
        (
            [
                [
                    '[{"Id":',
                    '"id_10_CPUCreditUsage",',
                    '"Label":',
                    '"172.31.41.207-eu-central-1-i-08363bfeff774e12c",',
                    '"Timestamps":',
                    '["2020-12-01',
                    '12:24:00+00:00"],',
                    '"Values":',
                    "[[0.0030055,",
                    "null]],",
                    '"StatusCode":',
                    '"Complete"},',
                    '{"Id":',
                    '"id_10_CPUCreditBalance",',
                    '"Label":',
                    '"172.31.41.207-eu-central-1-i-08363bfeff774e12c",',
                    '"Timestamps":',
                    '["2020-12-01',
                    '12:24:00+00:00"],',
                    '"Values":',
                    "[[29.5837305,",
                    "null]],",
                    '"StatusCode":',
                    '"Complete"},',
                    '{"Id":',
                    '"id_10_CPUUtilization",',
                    '"Label":',
                    '"172.31.41.207-eu-central-1-i-08363bfeff774e12c",',
                    '"Timestamps":',
                    '["2020-12-01',
                    '12:24:00+00:00"],',
                    '"Values":',
                    "[[0.0499999999999995,",
                    "null]],",
                    '"StatusCode":',
                    '"Complete"},',
                    '{"Id":',
                    '"id_10_DiskReadOps",',
                    '"Label":',
                    '"172.31.41.207-eu-central-1-i-08363bfeff774e12c",',
                    '"Timestamps":',
                    '["2020-12-01',
                    '12:24:00+00:00"],',
                    '"Values":',
                    "[[0.0,",
                    "null]],",
                    '"StatusCode":',
                    '"Complete"},',
                    '{"Id":',
                    '"id_10_DiskWriteOps",',
                    '"Label":',
                    '"172.31.41.207-eu-central-1-i-08363bfeff774e12c",',
                    '"Timestamps":',
                    '["2020-12-01',
                    '12:24:00+00:00"],',
                    '"Values":',
                    "[[0.0,",
                    "null]],",
                    '"StatusCode":',
                    '"Complete"},',
                    '{"Id":',
                    '"id_10_DiskReadBytes",',
                    '"Label":',
                    '"172.31.41.207-eu-central-1-i-08363bfeff774e12c",',
                    '"Timestamps":',
                    '["2020-12-01',
                    '12:24:00+00:00"],',
                    '"Values":',
                    "[[0.0,",
                    "null]],",
                    '"StatusCode":',
                    '"Complete"},',
                    '{"Id":',
                    '"id_10_DiskWriteBytes",',
                    '"Label":',
                    '"172.31.41.207-eu-central-1-i-08363bfeff774e12c",',
                    '"Timestamps":',
                    '["2020-12-01',
                    '12:24:00+00:00"],',
                    '"Values":',
                    "[[0.0,",
                    "null]],",
                    '"StatusCode":',
                    '"Complete"},',
                    '{"Id":',
                    '"id_10_NetworkIn",',
                    '"Label":',
                    '"172.31.41.207-eu-central-1-i-08363bfeff774e12c",',
                    '"Timestamps":',
                    '["2020-12-01',
                    '12:24:00+00:00"],',
                    '"Values":',
                    "[[702.2,",
                    "null]],",
                    '"StatusCode":',
                    '"Complete"},',
                    '{"Id":',
                    '"id_10_NetworkOut",',
                    '"Label":',
                    '"172.31.41.207-eu-central-1-i-08363bfeff774e12c",',
                    '"Timestamps":',
                    '["2020-12-01',
                    '12:24:00+00:00"],',
                    '"Values":',
                    "[[369.0,",
                    "null]],",
                    '"StatusCode":',
                    '"Complete"},',
                    '{"Id":',
                    '"id_10_StatusCheckFailed_Instance",',
                    '"Label":',
                    '"172.31.41.207-eu-central-1-i-08363bfeff774e12c",',
                    '"Timestamps":',
                    '["2020-12-01',
                    '12:24:00+00:00"],',
                    '"Values":',
                    "[[0.0,",
                    "null]],",
                    '"StatusCode":',
                    '"Complete"},',
                    '{"Id":',
                    '"id_10_StatusCheckFailed_System",',
                    '"Label":',
                    '"172.31.41.207-eu-central-1-i-08363bfeff774e12c",',
                    '"Timestamps":',
                    '["2020-12-01',
                    '12:24:00+00:00"],',
                    '"Values":',
                    "[[0.0,",
                    "null]],",
                    '"StatusCode":',
                    '"Complete"}]',
                ]
            ],
            [
                {
                    "Id": "id_10_CPUCreditUsage",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:24:00+00:00"],
                    "Values": [[0.0030055, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_CPUCreditBalance",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:24:00+00:00"],
                    "Values": [[29.5837305, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_CPUUtilization",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:24:00+00:00"],
                    "Values": [[0.0499999999999995, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_DiskReadOps",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:24:00+00:00"],
                    "Values": [[0.0, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_DiskWriteOps",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:24:00+00:00"],
                    "Values": [[0.0, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_DiskReadBytes",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:24:00+00:00"],
                    "Values": [[0.0, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_DiskWriteBytes",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:24:00+00:00"],
                    "Values": [[0.0, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_NetworkIn",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:24:00+00:00"],
                    "Values": [[702.2, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_NetworkOut",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:24:00+00:00"],
                    "Values": [[369.0, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_StatusCheckFailed_Instance",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:24:00+00:00"],
                    "Values": [[0.0, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_StatusCheckFailed_System",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:24:00+00:00"],
                    "Values": [[0.0, None]],
                    "StatusCode": "Complete",
                },
            ],
        ),
        (
            [
                [
                    '[{"Description":',
                    '"Joerg',
                    "Herbels",
                    "security",
                    'group",',
                    '"GroupName":',
                    '"joerg.herbel.secgroup",',
                    '"IpPermissions":',
                    '[{"FromPort":',
                    "80,",
                    '"IpProtocol":',
                    '"tcp",',
                    '"IpRanges":',
                    '[{"CidrIp":',
                    '"0.0.0.0/0"}],',
                    '"Ipv6Ranges":',
                    '[{"CidrIpv6":',
                    '"::/0"}],',
                    '"PrefixListIds":',
                    "[],",
                    '"ToPort":',
                    "80,",
                    '"UserIdGroupPairs":',
                    '[{"GroupId":',
                    '"sg-06368b02de2a8b850",',
                    '"UserId":',
                    '"710145618630"}]},',
                    '{"FromPort":',
                    "0,",
                    '"IpProtocol":',
                    '"tcp",',
                    '"IpRanges":',
                    '[{"CidrIp":',
                    '"0.0.0.0/0"}],',
                    '"Ipv6Ranges":',
                    "[],",
                    '"PrefixListIds":',
                    "[],",
                    '"ToPort":',
                    "65535,",
                    '"UserIdGroupPairs":',
                    "[]},",
                    '{"FromPort":',
                    "80,",
                    '"IpProtocol":',
                    '"tcp",',
                    '"IpRanges":',
                    '[{"CidrIp":',
                    '"0.0.0.0/0"}],',
                    '"Ipv6Ranges":',
                    '[{"CidrIpv6":',
                    '"::/0"}],',
                    '"PrefixListIds":',
                    "[],",
                    '"ToPort":',
                    "90,",
                    '"UserIdGroupPairs":',
                    "[]},",
                    '{"IpProtocol":',
                    '"-1",',
                    '"IpRanges":',
                    "[],",
                    '"Ipv6Ranges":',
                    "[],",
                    '"PrefixListIds":',
                    "[],",
                    '"UserIdGroupPairs":',
                    '[{"GroupId":',
                    '"sg-06368b02de2a8b850",',
                    '"UserId":',
                    '"710145618630"}]},',
                    '{"FromPort":',
                    "22,",
                    '"IpProtocol":',
                    '"tcp",',
                    '"IpRanges":',
                    '[{"CidrIp":',
                    '"0.0.0.0/0"}],',
                    '"Ipv6Ranges":',
                    '[{"CidrIpv6":',
                    '"::/0"}],',
                    '"PrefixListIds":',
                    "[],",
                    '"ToPort":',
                    "22,",
                    '"UserIdGroupPairs":',
                    "[]},",
                    '{"FromPort":',
                    "5000,",
                    '"IpProtocol":',
                    '"tcp",',
                    '"IpRanges":',
                    '[{"CidrIp":',
                    '"0.0.0.0/0"}],',
                    '"Ipv6Ranges":',
                    '[{"CidrIpv6":',
                    '"::/0"}],',
                    '"PrefixListIds":',
                    "[],",
                    '"ToPort":',
                    "5000,",
                    '"UserIdGroupPairs":',
                    "[]},",
                    '{"FromPort":',
                    "3389,",
                    '"IpProtocol":',
                    '"tcp",',
                    '"IpRanges":',
                    '[{"CidrIp":',
                    '"0.0.0.0/0"}],',
                    '"Ipv6Ranges":',
                    '[{"CidrIpv6":',
                    '"::/0"}],',
                    '"PrefixListIds":',
                    "[],",
                    '"ToPort":',
                    "3389,",
                    '"UserIdGroupPairs":',
                    "[]}],",
                    '"OwnerId":',
                    '"710145618630",',
                    '"GroupId":',
                    '"sg-06368b02de2a8b850",',
                    '"IpPermissionsEgress":',
                    '[{"IpProtocol":',
                    '"-1",',
                    '"IpRanges":',
                    '[{"CidrIp":',
                    '"0.0.0.0/0"}],',
                    '"Ipv6Ranges":',
                    "[],",
                    '"PrefixListIds":',
                    "[],",
                    '"UserIdGroupPairs":',
                    "[]}],",
                    '"VpcId":',
                    '"vpc-dc8ba3b7"}]',
                ]
            ],
            [
                {
                    "Description": "Joerg Herbels security group",
                    "GroupName": "joerg.herbel.secgroup",
                    "IpPermissions": [
                        {
                            "FromPort": 80,
                            "IpProtocol": "tcp",
                            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                            "Ipv6Ranges": [{"CidrIpv6": "::/0"}],
                            "PrefixListIds": [],
                            "ToPort": 80,
                            "UserIdGroupPairs": [
                                {"GroupId": "sg-06368b02de2a8b850", "UserId": "710145618630"}
                            ],
                        },
                        {
                            "FromPort": 0,
                            "IpProtocol": "tcp",
                            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                            "Ipv6Ranges": [],
                            "PrefixListIds": [],
                            "ToPort": 65535,
                            "UserIdGroupPairs": [],
                        },
                        {
                            "FromPort": 80,
                            "IpProtocol": "tcp",
                            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                            "Ipv6Ranges": [{"CidrIpv6": "::/0"}],
                            "PrefixListIds": [],
                            "ToPort": 90,
                            "UserIdGroupPairs": [],
                        },
                        {
                            "IpProtocol": "-1",
                            "IpRanges": [],
                            "Ipv6Ranges": [],
                            "PrefixListIds": [],
                            "UserIdGroupPairs": [
                                {"GroupId": "sg-06368b02de2a8b850", "UserId": "710145618630"}
                            ],
                        },
                        {
                            "FromPort": 22,
                            "IpProtocol": "tcp",
                            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                            "Ipv6Ranges": [{"CidrIpv6": "::/0"}],
                            "PrefixListIds": [],
                            "ToPort": 22,
                            "UserIdGroupPairs": [],
                        },
                        {
                            "FromPort": 5000,
                            "IpProtocol": "tcp",
                            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                            "Ipv6Ranges": [{"CidrIpv6": "::/0"}],
                            "PrefixListIds": [],
                            "ToPort": 5000,
                            "UserIdGroupPairs": [],
                        },
                        {
                            "FromPort": 3389,
                            "IpProtocol": "tcp",
                            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                            "Ipv6Ranges": [{"CidrIpv6": "::/0"}],
                            "PrefixListIds": [],
                            "ToPort": 3389,
                            "UserIdGroupPairs": [],
                        },
                    ],
                    "OwnerId": "710145618630",
                    "GroupId": "sg-06368b02de2a8b850",
                    "IpPermissionsEgress": [
                        {
                            "IpProtocol": "-1",
                            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                            "Ipv6Ranges": [],
                            "PrefixListIds": [],
                            "UserIdGroupPairs": [],
                        }
                    ],
                    "VpcId": "vpc-dc8ba3b7",
                }
            ],
        ),
    ],
)
def test_parse_aws(string_table: StringTable, expected_result: GenericAWSSection) -> None:
    assert parse_aws(string_table) == expected_result


def test_parse_aws_limits_generic() -> None:
    parsed = parse_aws_limits_generic(
        string_table=[
            [
                '[["topics_standard",',
                '"Standard',
                "Topics",
                'Limit",',
                "100000,",
                "2,",
                '"eu-central-1"],',
                '["topics_fifo",',
                '"FIFO',
                "Topics",
                'Limit",',
                "1000,",
                "1,",
                '"eu-central-1"],',
                '["subscriptions_of_topic_AutoTag",',
                '"Subscriptions',
                "Limit",
                "for",
                "Topic",
                'AutoTag",',
                "12500000,",
                "3,",
                '"eu-central-1"],',
                '["subscriptions_of_topic_TestTopicTim.fifo",',
                '"Subscriptions',
                "Limit",
                "for",
                "Topic",
                'TestTopicTim.fifo",',
                "100,",
                "0,",
                '"eu-central-1"],',
                '["subscriptions_of_topic_dynamodb",',
                '"Subscriptions',
                "Limit",
                "for",
                "Topic",
                'dynamodb",',
                "12500000,",
                "0,",
                '"eu-central-1"]]',
            ]
        ]
    )
    assert len(parsed) == 1
    limits = parsed["eu-central-1"]
    limits = [v[:-1] for v in limits]
    assert limits == [
        ["topics_standard", "Standard Topics Limit", 100000, 2],
        ["topics_fifo", "FIFO Topics Limit", 1000, 1],
        [
            "subscriptions_of_topic_AutoTag",
            "Subscriptions Limit for Topic AutoTag",
            12500000,
            3,
        ],
        [
            "subscriptions_of_topic_TestTopicTim.fifo",
            "Subscriptions Limit for Topic TestTopicTim.fifo",
            100,
            0,
        ],
        [
            "subscriptions_of_topic_dynamodb",
            "Subscriptions Limit for Topic dynamodb",
            12500000,
            0,
        ],
    ]


@pytest.mark.parametrize(
    "test_input, output",
    [
        (
            [
                ["topics_standard", "Standard Topics Limit", 100000, 2, str],
                ["topics_fifo", "FIFO Topics Limit", 1000, 1, str],
            ],
            [
                Metric("aws_sns_topics_standard", 2),
                Result(state=State.OK, notice="Standard Topics Limit: 2 (of max. 100000), <0.01%"),
                Metric("aws_sns_topics_fifo", 1),
                Result(state=State.OK, notice="FIFO Topics Limit: 1 (of max. 1000), 0.10%"),
            ],
        ),
        (
            [
                ["topics_standard", "Standard Topics Limit", 100000, 100001, str],
                ["topics_fifo", "FIFO Topics Limit", 1000, 1, str],
            ],
            [
                Metric("aws_sns_topics_standard", 100001),
                Result(
                    state=State.CRIT,
                    summary="Standard Topics Limit: 100001 (of max. 100000), 100.00% (warn/crit at 80.00%/90.00%)",
                ),
                Metric("aws_sns_topics_fifo", 1),
                Result(state=State.OK, notice="FIFO Topics Limit: 1 (of max. 1000), 0.10%"),
            ],
        ),
        (
            [
                ["topics_standard", "Standard Topics Limit", 100000, 2, str],
                ["topics_fifo", "FIFO Topics Limit", 1000, 1001, str],
            ],
            [
                Metric("aws_sns_topics_standard", 2),
                Result(state=State.OK, notice="Standard Topics Limit: 2 (of max. 100000), <0.01%"),
                Metric("aws_sns_topics_fifo", 1001),
                Result(
                    state=State.CRIT,
                    summary="FIFO Topics Limit: 1001 (of max. 1000), 100.10% (warn/crit at 80.00%/90.00%)",
                ),
            ],
        ),
        (
            [
                ["topics_standard", "Standard Topics Limit", 100000, 100001, str],
                ["topics_fifo", "FIFO Topics Limit", 1000, 1001, str],
            ],
            [
                Metric("aws_sns_topics_standard", 100001),
                Result(
                    state=State.CRIT,
                    summary="Standard Topics Limit: 100001 (of max. 100000), 100.00% (warn/crit at 80.00%/90.00%)",
                ),
                Metric("aws_sns_topics_fifo", 1001),
                Result(
                    state=State.CRIT,
                    summary="FIFO Topics Limit: 1001 (of max. 1000), 100.10% (warn/crit at 80.00%/90.00%)",
                ),
            ],
        ),
    ],
)
def test_check_aws_limits_legacy(test_input: list[list], output: CheckResult) -> None:
    assert (
        list(
            check_aws_limits_legacy(
                "sns",
                {
                    "topics_fifo": (None, 80.0, 90.0),
                    "topics_standard": (None, 80.0, 90.0),
                },
                test_input,
            )
        )
        == output
    )


@pytest.mark.parametrize(
    "test_input, output",
    [
        (
            [
                ["topics_standard", "Standard Topics Limit", 100000, 2, str],
                ["topics_fifo", "FIFO Topics Limit", 1000, 1, str],
            ],
            [
                Metric("aws_sns_topics_standard", 2),
                Result(state=State.OK, notice="Standard Topics Limit: 2 (of max. 100000), <0.01%"),
                Metric("aws_sns_topics_fifo", 1),
                Result(state=State.OK, notice="FIFO Topics Limit: 1 (of max. 1000), 0.10%"),
            ],
        ),
        (
            [
                ["topics_standard", "Standard Topics Limit", 100000, 100001, str],
                ["topics_fifo", "FIFO Topics Limit", 1000, 1, str],
            ],
            [
                Metric("aws_sns_topics_standard", 100001),
                Result(
                    state=State.CRIT,
                    summary="Standard Topics Limit: 100001 (of max. 100000), 100.00% (warn/crit at 80.00%/90.00%)",
                ),
                Metric("aws_sns_topics_fifo", 1),
                Result(state=State.OK, notice="FIFO Topics Limit: 1 (of max. 1000), 0.10%"),
            ],
        ),
        (
            [
                ["topics_standard", "Standard Topics Limit", 100000, 2, str],
                ["topics_fifo", "FIFO Topics Limit", 1000, 1001, str],
            ],
            [
                Metric("aws_sns_topics_standard", 2),
                Result(state=State.OK, notice="Standard Topics Limit: 2 (of max. 100000), <0.01%"),
                Metric("aws_sns_topics_fifo", 1001),
                Result(
                    state=State.CRIT,
                    summary="FIFO Topics Limit: 1001 (of max. 1000), 100.10% (warn/crit at 80.00%/90.00%)",
                ),
            ],
        ),
        (
            [
                ["topics_standard", "Standard Topics Limit", 100000, 100001, str],
                ["topics_fifo", "FIFO Topics Limit", 1000, 1001, str],
            ],
            [
                Metric("aws_sns_topics_standard", 100001),
                Result(
                    state=State.CRIT,
                    summary="Standard Topics Limit: 100001 (of max. 100000), 100.00% (warn/crit at 80.00%/90.00%)",
                ),
                Metric("aws_sns_topics_fifo", 1001),
                Result(
                    state=State.CRIT,
                    summary="FIFO Topics Limit: 1001 (of max. 1000), 100.10% (warn/crit at 80.00%/90.00%)",
                ),
            ],
        ),
    ],
)
def test_check_aws_limits(test_input: list[list], output: CheckResult) -> None:
    default_limit: AWSLimits = {
        "absolute": ("aws_default_limit", None),
        "percentage": {"warn": 80.0, "crit": 90.0},
    }
    assert (
        list(
            check_aws_limits(
                "sns",
                {
                    "topics_fifo": ("set_levels", default_limit),
                    "topics_standard": ("set_levels", default_limit),
                },
                test_input,
            )
        )
        == output
    )


@pytest.mark.parametrize(
    "expected_metric_names, section, extra_kwargs, expected_result",
    [
        (
            [
                "CPUCreditUsage",
                "CPUCreditBalance",
                "CPUUtilization",
                "DiskReadOps",
                "DiskWriteOps",
                "DiskReadBytes",
                "DiskWriteBytes",
                "NetworkIn",
                "NetworkOut",
                "StatusCheckFailed_Instance",
                "StatusCheckFailed_System",
            ],
            [
                {
                    "Id": "id_10_CPUCreditUsage",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:45:00+00:00"],
                    "Values": [[0.0021155, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_CPUCreditBalance",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:45:00+00:00"],
                    "Values": [[31.5750585, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_CPUUtilization",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:45:00+00:00"],
                    "Values": [[0.0322580645161318, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_DiskReadOps",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:45:00+00:00"],
                    "Values": [[0.0, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_DiskWriteOps",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:45:00+00:00"],
                    "Values": [[0.0, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_DiskReadBytes",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:45:00+00:00"],
                    "Values": [[0.0, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_DiskWriteBytes",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:45:00+00:00"],
                    "Values": [[0.0, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_NetworkIn",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:45:00+00:00"],
                    "Values": [[840.4, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_NetworkOut",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:45:00+00:00"],
                    "Values": [[466.0, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_StatusCheckFailed_Instance",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:45:00+00:00"],
                    "Values": [[0.0, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_10_StatusCheckFailed_System",
                    "Label": "172.31.41.207-eu-central-1-i-08363bfeff774e12c",
                    "Timestamps": ["2020-12-01 12:45:00+00:00"],
                    "Values": [[0.0, None]],
                    "StatusCode": "Complete",
                },
            ],
            {},
            {
                "172.31.41.207-eu-central-1-i-08363bfeff774e12c": {
                    "CPUCreditUsage": 0.0021155,
                    "CPUCreditBalance": 31.5750585,
                    "CPUUtilization": 0.0322580645161318,
                    "DiskReadOps": 0.0,
                    "DiskWriteOps": 0.0,
                    "DiskReadBytes": 0.0,
                    "DiskWriteBytes": 0.0,
                    "NetworkIn": 840.4,
                    "NetworkOut": 466.0,
                    "StatusCheckFailed_Instance": 0.0,
                    "StatusCheckFailed_System": 0.0,
                }
            },
        ),
        (
            [
                "Requests",
                "BytesDownloaded",
                "BytesUploaded",
                "TotalErrorRate",
                "4xxErrorRate",
                "5xxErrorRate",
            ],
            [
                {
                    "Id": "id_0_Requests",
                    "Label": "E2RAYOVSSL6ZM3",
                    "Timestamps": [],
                    "Values": [],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_0_BytesDownloaded",
                    "Label": "E2RAYOVSSL6ZM3",
                    "Timestamps": [],
                    "Values": [],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_0_BytesUploaded",
                    "Label": "E2RAYOVSSL6ZM3",
                    "Timestamps": [],
                    "Values": [],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_0_TotalErrorRate",
                    "Label": "E2RAYOVSSL6ZM3",
                    "Timestamps": [],
                    "Values": [],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_0_4xxErrorRate",
                    "Label": "E2RAYOVSSL6ZM3",
                    "Timestamps": [],
                    "Values": [],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_0_5xxErrorRate",
                    "Label": "E2RAYOVSSL6ZM3",
                    "Timestamps": [],
                    "Values": [],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_1_Requests",
                    "Label": "EWN6C0UT7HBX0",
                    "Timestamps": ["2022-04-29 13:35:00+00:00"],
                    "Values": [[88.0, 600]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_1_BytesDownloaded",
                    "Label": "EWN6C0UT7HBX0",
                    "Timestamps": ["2022-04-29 13:35:00+00:00"],
                    "Values": [[582911.0, 600]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_1_BytesUploaded",
                    "Label": "EWN6C0UT7HBX0",
                    "Timestamps": ["2022-04-29 13:35:00+00:00"],
                    "Values": [[0.0, 600]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_1_TotalErrorRate",
                    "Label": "EWN6C0UT7HBX0",
                    "Timestamps": ["2022-04-29 13:35:00+00:00"],
                    "Values": [[0.0, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_1_4xxErrorRate",
                    "Label": "EWN6C0UT7HBX0",
                    "Timestamps": ["2022-04-29 13:35:00+00:00"],
                    "Values": [[0.0, None]],
                    "StatusCode": "Complete",
                },
                {
                    "Id": "id_1_5xxErrorRate",
                    "Label": "EWN6C0UT7HBX0",
                    "Timestamps": ["2022-04-29 13:35:00+00:00"],
                    "Values": [[0.0, None]],
                    "StatusCode": "Complete",
                },
            ],
            {"convert_sum_stats_to_rate": False},
            {
                "EWN6C0UT7HBX0": {
                    "Requests": 88.0,
                    "BytesDownloaded": 582911.0,
                    "BytesUploaded": 0.0,
                    "TotalErrorRate": 0.0,
                    "4xxErrorRate": 0.0,
                    "5xxErrorRate": 0.0,
                }
            },
        ),
    ],
)
def test_extract_aws_metrics_by_labels(
    expected_metric_names, section, extra_kwargs, expected_result
):
    assert (
        extract_aws_metrics_by_labels(expected_metric_names, section, **extra_kwargs)
        == expected_result
    )


SECTION_AWS_LAMBDA_SUMMARY: LambdaSummarySection = {
    "calling_other_lambda_concurrently [eu-central-1]": LambdaFunctionConfiguration(
        Timeout=1.0, MemorySize=128.0, CodeSize=483.0
    ),
    "my_python_test_function [eu-central-1]": LambdaFunctionConfiguration(
        Timeout=1.0, MemorySize=128.0, CodeSize=483.0
    ),
    "myLambdaTestFunction [eu-north-1]": LambdaFunctionConfiguration(
        Timeout=1.0, MemorySize=128.0, CodeSize=299.0
    ),
}

SECTION_AWS_LAMBDA_CLOUDWATCH_INSIGHTS: CloudwatchInsightsSection = {
    "calling_other_lambda_concurrently [eu-central-1]": LambdaInsightMetrics(
        max_memory_used_bytes=128000000.0,
        count_cold_starts_in_percent=50.0,
        max_init_duration_seconds=0.33964999999999995,
    ),
    "my_python_test_function [eu-central-1]": LambdaInsightMetrics(
        max_memory_used_bytes=52000000.0,
        count_cold_starts_in_percent=50.0,
        max_init_duration_seconds=1.62853,
    ),
}


def test_display_order_logic() -> None:
    # Assemble
    display_regions = [display_region for _region_id, display_region in aws_region_to_monitor()]
    # Assert
    # GovCloud entries are generally useful to only very few people. Thus, they should all be
    # displayed at end of the list. Within the groups, the order should be alphabetical.
    assert display_regions == [
        *sorted(region for region in display_regions if "GovCloud" not in region),
        *sorted(region for region in display_regions if "GovCloud" in region),
    ]

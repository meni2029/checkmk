#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from argparse import Namespace as Args
from collections.abc import Mapping, Sequence
from typing import Protocol

import pytest

from cmk.plugins.aws.special_agent.agent_aws import (
    AWSConfig,
    EC2,
    EC2Labels,
    EC2Limits,
    EC2SecurityGroups,
    EC2Summary,
    NamingConvention,
    OverallTags,
    ResultDistributor,
    TagsImportPatternOption,
    TagsOption,
)

from .agent_aws_fake_clients import (
    EC2DescribeAddressesIB,
    EC2DescribeInstancesIB,
    EC2DescribeNetworkInterfacesIB,
    EC2DescribeReservedInstancesIB,
    EC2DescribeSecurityGroupsIB,
    EC2DescribeSpotFleetRequestsIB,
    EC2DescribeSpotInstanceRequestsIB,
    FakeCloudwatchClient,
    FakeServiceQuotasClient,
)


class FakeEC2Client:
    def __init__(self, skip_entities: Mapping[str, object] | None = None) -> None:
        self._skip_entities = {} if not skip_entities else skip_entities

    def describe_instances(self, InstanceIds=None, Filters=None):
        instances = EC2DescribeInstancesIB.create_instances(
            amount=3, skip_entities=self._skip_entities.get("Instances")
        )

        for instance in instances:
            if instance["InstanceId"] == "InstanceId-0":
                continue
            instance["Tags"] = []

        return {
            "Reservations": [
                {
                    "Groups": [
                        {"GroupName": "string", "GroupId": "string"},
                    ],
                    "Instances": instances,
                    "OwnerId": "string",
                    "RequesterId": "string",
                    "ReservationId": "string",
                },
            ],
            "NextToken": "string",
        }

    def describe_reserved_instances(self):
        return {
            "ReservedInstances": EC2DescribeReservedInstancesIB.create_instances(
                amount=3,
                skip_entities=self._skip_entities.get("ReservedInstances", []),
            ),
        }

    def describe_addresses(self):
        return {
            "Addresses": EC2DescribeAddressesIB.create_instances(amount=3),
        }

    def describe_security_groups(self, InstanceIds=None, Filters=None):
        return {
            "SecurityGroups": EC2DescribeSecurityGroupsIB.create_instances(amount=3),
            "NextToken": "string",
        }

    def describe_network_interfaces(self):
        return {
            "NetworkInterfaces": EC2DescribeNetworkInterfacesIB.create_instances(amount=3),
            "NextToken": "string",
        }

    def describe_spot_instance_requests(self):
        return {
            "SpotInstanceRequests": EC2DescribeSpotInstanceRequestsIB.create_instances(amount=3),
            "NextToken": "string",
        }

    def describe_spot_fleet_requests(self):
        return {
            "SpotFleetRequestConfigs": EC2DescribeSpotFleetRequestsIB.create_instances(amount=3),
            "NextToken": "string",
        }


EC2SectionsOut = tuple[EC2Limits, EC2Summary, EC2Labels, EC2SecurityGroups, EC2]


class EC2Sections(Protocol):
    def __call__(
        self,
        names: object | None = None,
        tags: OverallTags = (None, None),
        skip_entities: Mapping[str, object] | None = None,
        tag_import: TagsOption = TagsImportPatternOption.import_all,
    ) -> EC2SectionsOut: ...


@pytest.fixture()
def get_ec2_sections() -> EC2Sections:
    def _create_ec2_sections(
        names: object | None = None,
        tags: OverallTags = (None, None),
        skip_entities: Mapping[str, object] | None = None,
        tag_import: TagsOption = TagsImportPatternOption.import_all,
    ) -> EC2SectionsOut:
        region = "region"
        config = AWSConfig(
            "hostname", Args(), ([], []), NamingConvention.ip_region_instance, tag_import
        )
        config.add_single_service_config("ec2_names", names)
        config.add_service_tags("ec2_tags", tags)
        fake_ec2_client = FakeEC2Client(skip_entities)
        fake_cloudwatch_client = FakeCloudwatchClient()
        fake_service_quotas_client = FakeServiceQuotasClient()

        distributor = ResultDistributor()

        # TODO: FakeEC2Client shoud actually subclass EC2Client, etc.
        ec2_limits = EC2Limits(
            fake_ec2_client,  # type: ignore[arg-type]
            region,
            config,
            distributor,
            fake_service_quotas_client,  # type: ignore[arg-type]
        )
        ec2_summary = EC2Summary(fake_ec2_client, region, config, distributor)  # type: ignore[arg-type]
        ec2_labels = EC2Labels(fake_ec2_client, region, config)  # type: ignore[arg-type]
        ec2_security_groups = EC2SecurityGroups(fake_ec2_client, region, config)  # type: ignore[arg-type]
        ec2 = EC2(fake_cloudwatch_client, region, config)  # type: ignore[arg-type]

        distributor.add(ec2_limits.name, ec2_summary)
        distributor.add(ec2_summary.name, ec2_labels)
        distributor.add(ec2_summary.name, ec2_security_groups)
        distributor.add(ec2_summary.name, ec2)
        return ec2_limits, ec2_summary, ec2_labels, ec2_security_groups, ec2

    return _create_ec2_sections


ec2_params = [
    (None, (None, None), 3, 1),
    (None, ([["Key-0"]], [["Value-0"]]), 1, 1),
    (None, ([["Key-X"]], [["Value-0"]]), 0, 0),
    (None, ([["Key-0"]], [["Value-X"]]), 0, 0),
    (None, ([["Key-0"]], [["Value-1"]]), 0, 0),
    (None, ([["Key-1"]], [["Value-0", "Value-1"]]), 1, 1),
    (None, ([["Key-0"]], [["Value-0", "Value-1"]]), 1, 1),
    (["InstanceId-0"], (None, None), 1, 1),
    (["InstanceId-0", "Foo", "Bar"], (None, None), 1, 1),
    (["InstanceId-0", "InstanceId-1"], (None, None), 2, 1),
    (["InstanceId-0", "InstanceId-1", "Foo", "Bar"], (None, None), 2, 1),
    (["InstanceId-0", "InstanceId-1", "InstanceId-2"], (None, None), 3, 1),
    (["InstanceId-0", "InstanceId-1", "InstanceId-2", "Foo", "Bar"], (None, None), 3, 1),
    (["Foo", "Bar"], (None, None), 0, 0),
]


@pytest.mark.parametrize("names,tags,found_ec2,found_ec2_with_labels", ec2_params)
def test_agent_aws_ec2_limits(
    get_ec2_sections: EC2Sections,
    names: Sequence[str] | None,
    tags: OverallTags,
    found_ec2: int,
    found_ec2_with_labels: int,
) -> None:
    ec2_limits, _ec2_summary, _ec2_labels, _ec2_security_groups, _ec2 = get_ec2_sections(
        names, tags
    )
    ec2_limits_results = ec2_limits.run().results

    assert ec2_limits.cache_interval == 300
    assert ec2_limits.period == 600
    assert ec2_limits.name == "ec2_limits"
    assert len(ec2_limits_results) == 1

    for result in ec2_limits_results:
        assert result.piggyback_hostname == ""
        for limit in result.content:
            assert limit.key in [
                "vpc_elastic_ip_addresses",
                "elastic_ip_addresses",
                "spot_inst_requests",
                "active_spot_fleet_requests",
                "spot_fleet_total_target_capacity",
                "vpc_sec_group_rules",
                "vpc_sec_groups",
                "if_vpc_sec_group",
            ] or limit.key.startswith("running_ondemand_instances_")


@pytest.mark.parametrize("names,tags,found_ec2,found_ec2_with_labels", ec2_params)
def test_agent_aws_ec2_summary(
    get_ec2_sections: EC2Sections,
    names: Sequence[str] | None,
    tags: OverallTags,
    found_ec2: int,
    found_ec2_with_labels: int,
) -> None:
    ec2_limits, ec2_summary, _ec2_labels, _ec2_security_groups, _ec2 = get_ec2_sections(names, tags)
    _ec2_limits_results = ec2_limits.run().results
    ec2_summary_results = ec2_summary.run().results

    assert ec2_summary.cache_interval == 300
    assert ec2_summary.period == 600
    assert ec2_summary.name == "ec2_summary"

    if found_ec2:
        assert len(ec2_summary_results) == 1

        result = ec2_summary_results[0]
        assert result.piggyback_hostname == ""
        assert len(result.content) == found_ec2

    else:
        assert len(ec2_summary_results) == 0


@pytest.mark.parametrize("names,tags,found_ec2,found_ec2_with_labels", ec2_params)
def test_agent_aws_ec2_labels(
    get_ec2_sections: EC2Sections,
    names: Sequence[str] | None,
    tags: OverallTags,
    found_ec2: int,
    found_ec2_with_labels: int,
) -> None:
    ec2_limits, ec2_summary, ec2_labels, _ec2_security_groups, _ec2 = get_ec2_sections(names, tags)
    _ec2_limits_results = ec2_limits.run().results
    _ec2_summary_results = ec2_summary.run().results
    ec2_labels_results = ec2_labels.run().results

    assert ec2_labels.cache_interval == 300
    assert ec2_labels.period == 600
    assert ec2_labels.name == "ec2_labels"

    assert len(ec2_labels_results) == found_ec2_with_labels


@pytest.mark.parametrize("names,tags,found_ec2,found_ec2_with_labels", ec2_params)
def test_agent_aws_ec2_security_groups(
    get_ec2_sections: EC2Sections,
    names: Sequence[str] | None,
    tags: OverallTags,
    found_ec2: int,
    found_ec2_with_labels: int,
) -> None:
    ec2_limits, ec2_summary, _ec2_labels, ec2_security_groups, _ec2 = get_ec2_sections(names, tags)
    _ec2_limits_results = ec2_limits.run().results
    _ec2_summary_results = ec2_summary.run().results
    ec2_security_groups_results = ec2_security_groups.run().results

    assert ec2_security_groups.cache_interval == 300
    assert ec2_security_groups.period == 600
    assert ec2_security_groups.name == "ec2_security_groups"

    assert len(ec2_security_groups_results) == found_ec2

    for result in ec2_security_groups_results:
        assert result.piggyback_hostname != ""


@pytest.mark.parametrize("names,tags,found_ec2,found_ec2_with_labels", ec2_params)
def test_agent_aws_ec2(
    get_ec2_sections: EC2Sections,
    names: Sequence[str] | None,
    tags: OverallTags,
    found_ec2: int,
    found_ec2_with_labels: int,
) -> None:
    ec2_limits, ec2_summary, _ec2_labels, _ec2_security_groups, ec2 = get_ec2_sections(names, tags)
    _ec2_limits_results = ec2_limits.run().results
    _ec2_summary_results = ec2_summary.run().results
    ec2_results = ec2.run().results

    assert ec2.cache_interval == 300
    assert ec2.period == 600
    assert ec2.name == "ec2"

    assert len(ec2_results) == found_ec2

    for result in ec2_results:
        assert result.piggyback_hostname != ""

        # 11 metrics
        assert len(result.content) == 11


def test_agent_aws_ec2_summary_without_limits(
    get_ec2_sections: EC2Sections,
) -> None:
    _ec2_limits, ec2_summary, _ec2_labels, _ec2_security_groups, _ec2 = get_ec2_sections()
    ec2_summary_results = ec2_summary.run().results

    assert ec2_summary.cache_interval == 300
    assert ec2_summary.period == 600
    assert ec2_summary.name == "ec2_summary"

    assert len(ec2_summary_results) == 1

    result = ec2_summary_results[0]
    assert result.piggyback_hostname == ""
    assert len(result.content) == 3


def test_agent_aws_ec2_labels_without_limits(
    get_ec2_sections: EC2Sections,
) -> None:
    _ec2_limits, ec2_summary, ec2_labels, _ec2_security_groups, _ec2 = get_ec2_sections()
    _ec2_summary_results = ec2_summary.run().results
    ec2_labels_results = ec2_labels.run().results

    assert ec2_labels.cache_interval == 300
    assert ec2_labels.period == 600
    assert ec2_labels.name == "ec2_labels"

    assert len(ec2_labels_results) == 1


def test_agent_aws_ec2_security_groups_without_limits(
    get_ec2_sections: EC2Sections,
) -> None:
    _ec2_limits, ec2_summary, _ec2_labels, ec2_security_groups, _ec2 = get_ec2_sections()
    _ec2_summary_results = ec2_summary.run().results
    ec2_security_groups_results = ec2_security_groups.run().results

    assert ec2_security_groups.cache_interval == 300
    assert ec2_security_groups.period == 600
    assert ec2_security_groups.name == "ec2_security_groups"

    assert len(ec2_security_groups_results) == 3

    for result in ec2_security_groups_results:
        assert result.piggyback_hostname != ""


def test_agent_aws_ec2_without_limits(get_ec2_sections: EC2Sections) -> None:
    _ec2_limits, ec2_summary, _ec2_labels, _ec2_security_groups, ec2 = get_ec2_sections()
    _ec2_summary_results = ec2_summary.run().results
    ec2_results = ec2.run().results

    assert ec2.cache_interval == 300
    assert ec2.period == 600
    assert ec2.name == "ec2"

    assert len(ec2_results) == 3

    for result in ec2_results:
        assert result.piggyback_hostname != ""

        # 11 metrics
        assert len(result.content) == 11


@pytest.mark.parametrize("names,tags,found_ec2,found_ec2_with_labels", ec2_params)
@pytest.mark.parametrize(
    "skip_entities",
    [
        {"ReservedInstances": ["AvailabilityZone"]},
        {"Instances": ["Tags"]},  # Fix for FEED-6986
    ],
)
def test_agent_aws_ec2_no_crash_when_keys_missing(
    get_ec2_sections, names, tags, found_ec2, found_ec2_with_labels, skip_entities
):
    ec2_limits, ec2_summary, _ec2_labels, _ec2_security_groups, _ec2 = get_ec2_sections(
        names, tags, skip_entities=skip_entities
    )
    ec2_limits_results = ec2_limits.run().results
    ec2_summary.run()
    assert len(ec2_limits_results) == 1


@pytest.mark.parametrize(
    "tag_import, expected_tags",
    [
        (TagsImportPatternOption.import_all, ["Key-0", "Key-1", "Key-2"]),
        (r".*-1$", ["Key-1"]),
        (TagsImportPatternOption.ignore_all, []),
    ],
)
def test_agent_aws_ec2_filters_labels(
    get_ec2_sections: EC2Sections,
    tag_import: TagsOption,
    expected_tags: Sequence[str],
) -> None:
    _ec2_limits, ec2_summary, ec2_labels, _ec2_security_groups, _ec2 = get_ec2_sections(
        None, (None, None), tag_import=tag_import
    )
    ec2_summary_results = ec2_summary.run().results
    ec2_labels_results = ec2_labels.run().results

    if expected_tags:
        labels_row = ec2_labels_results[0].content
        assert list(labels_row.keys()) == expected_tags
    else:
        assert len(ec2_labels_results) == 0

    for result in ec2_summary_results:
        assert list(result.content[0]["TagsForCmkLabels"].keys()) == expected_tags

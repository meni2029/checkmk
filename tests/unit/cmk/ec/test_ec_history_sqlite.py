#!/usr/bin/env python3
# Copyright (C) 2023 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""EC History sqlite backend"""

import logging
import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from cmk.utils.hostaddress import HostName

import cmk.ec.export as ec
from cmk.ec.history_sqlite import filters_to_sqlite_query, history_file_to_sqlite, SQLiteHistory
from cmk.ec.main import StatusTableHistory
from cmk.ec.query import QueryFilter, QueryGET, StatusTable


@pytest.fixture(name="history_sqlite_raw")
def fixture_history_sqlite_raw() -> Iterator[sqlite3.Connection]:
    """history_sqlite_raw as an in :memory: database"""

    con = sqlite3.connect(":memory:")
    con.execute(
        """CREATE TABLE IF NOT EXISTS history
                             (time TEXT, what TEXT, who TEXT, addinfo TEXT, id INTEGER, count INTEGER, text TEXT, first FLOAT, last FLOAT,
                             comment TEXT, sl INTEGER, host TEXT, contact TEXT, application TEXT,
                             pid INTEGER, priority INTEGER, facility INTEGER, rule_id TEXT,
                             state INTEGER, phase TEXT, owner TEXT, match_groups TEXT,
                             contact_groups TEXT, ipaddress TEXT, orig_host TEXT,
                             contact_groups_precedence TEXT, core_host TEXT, host_in_downtime BOOL,
                             match_groups_syslog_application TEXT)"""
    )

    yield con

    con.execute("DROP TABLE IF EXISTS history")
    con.close()


def test_history_file_to_sqlite(tmp_path: Path, history_sqlite_raw: sqlite3.Connection) -> None:
    """History file saved correctly into sqlite inmemory DB."""

    path = tmp_path / "history_to_sqlite_test.log"
    path.write_text(
        """1666942211.07616	NEW			1002	1	some text	1666942208.0	1666942208.0		0	heute		OMD	0	6	9	asdf	0	open						host	heute	0	
1666942292.2998602	DELETE	cmkadmin		5	1	some text	1666942205.0	1666942205.0		0	heute		OMD	0	6	9	asdf	0	closed	cmkadmin					host	heute	0	
1666942292.2999856	DELETE	cmkadmin		6	1	some text	1666942205.0	1666942205.0		0	heute		OMD	0	6	9	asdf	0	closed	cmkadmin					host	heute	0	
1666942292.3000507	DELETE	cmkadmin		7	1	some text	1666942205.0	1666942205.0		0	heute		OMD	0	6	9	asdf	0	closed	cmkadmin					host	heute	0	"""
    )

    history_file_to_sqlite(path, history_sqlite_raw)

    cur = history_sqlite_raw.cursor()
    cur.execute("SELECT COUNT(*) FROM history;")
    assert cur.fetchone()[0] == 4


def test_history_file_to_sqlite_exceptions(
    tmp_path: Path, history_sqlite_raw: sqlite3.Connection
) -> None:
    """history_file_to_sqlite should raise exceptions."""
    path = tmp_path / "history_to_sqlite_test.log"
    path.write_text("malformed file")

    with pytest.raises(sqlite3.ProgrammingError):
        history_file_to_sqlite(path, history_sqlite_raw)


@pytest.mark.parametrize(
    "filters, expected_sqlite_query",
    [
        (
            [
                QueryFilter(
                    column_name="event_text",
                    operator_name="=",
                    predicate=lambda x: True,
                    argument="test_event",
                ),
            ],
            ("SELECT * FROM history WHERE text = ?;", ["test_event"]),
        ),
        (
            [
                QueryFilter(
                    column_name="event_time",
                    operator_name="<",
                    predicate=lambda x: True,
                    argument=123456789,
                ),
                QueryFilter(
                    column_name="event_time",
                    operator_name=">",
                    predicate=lambda x: True,
                    argument=1234,
                ),
            ],
            ("SELECT * FROM history WHERE time < ? AND time > ?;", [123456789, 1234]),
        ),
        (
            [
                QueryFilter(
                    column_name="history_who",
                    operator_name="~~",
                    predicate=lambda x: True,
                    argument="admin",
                ),
                QueryFilter(
                    column_name="event_owner",
                    operator_name="=~",
                    predicate=lambda x: True,
                    argument="user",
                ),
            ],
            ("SELECT * FROM history WHERE who LIKE '%?%' AND owner LIKE '%?%';", ["admin", "user"]),
        ),
    ],
)
def test_filters_to_sqlite_query(
    filters: list[QueryFilter], expected_sqlite_query: tuple[str, object]
) -> None:
    """filters_to_sqlite_query converts to correct sql select statement."""

    assert filters_to_sqlite_query(filters) == expected_sqlite_query


def test_filters_to_sqlite_query_raises_ValueError() -> None:
    """Wrong column name in filter raise ValueError."""

    wrong_filters = [
        QueryFilter(
            column_name="impossible_column_name",
            operator_name="=",
            predicate=lambda x: True,
            argument="test_event",
        )
    ]
    with pytest.raises(ValueError):
        filters_to_sqlite_query(wrong_filters)


def test_filters_to_sqlite_query_raises_KeyError() -> None:
    """Wrong operator name in filter raise KeyError."""

    wrong_filters = [
        QueryFilter(
            column_name="event_text",
            operator_name="=asdf or true;",  # type: ignore[arg-type]
            predicate=lambda x: True,
            argument="test_event",
        )
    ]
    with pytest.raises(KeyError):
        filters_to_sqlite_query(wrong_filters)


def test_basic_init_history_table(history_sqlite: SQLiteHistory) -> None:
    """Basic init in memory and history table exists."""

    cur = history_sqlite.conn.cursor()
    cur.row_factory = None
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='history';")
    assert cur.fetchall()[0] == ("history",)


def test_file_add_get(history_sqlite: SQLiteHistory) -> None:
    """Add 2 documents to history, get filtered result with 1 document."""

    event1 = ec.Event(
        host=HostName("ABC1"),
        text="Event1 text",
        core_host=HostName("ABC"),
        id=1,
        count=1,
        first=1.1,
        last=1.111,
        priority=100,
        host_in_downtime=False,
        contact_groups=("some string1", "another string1"),
    )
    event2 = ec.Event(
        host=HostName("ABC2"),
        text="Event2 text",
        core_host=HostName("ABC"),
        id=2,
        count=2,
        first=2.0,
        last=2.222,
        priority=200,
        host_in_downtime=True,
        contact_groups=("some string2", "another string2"),
    )

    history_sqlite.add(event=event1, what="NEW")
    history_sqlite.add(event=event2, what="NEW")

    logger = logging.getLogger("cmk.mkeventd")

    def get_table(name: str) -> StatusTable:
        assert name == "history"
        return StatusTableHistory(logger, history_sqlite)

    query = QueryGET(
        get_table,
        ["GET history", "Columns: history_what event_host", "Filter: event_host = ABC1"],
        logger,
    )

    query_result = history_sqlite.get(query)

    (row,) = query_result

    # check for several possible types: int, float, str, bool, list/tuple
    assert row["what"] == "NEW"  # type: ignore[call-overload]
    assert row["host"] == "ABC1"  # type: ignore[call-overload]
    assert row["id"] == 1  # type: ignore[call-overload]
    assert row["count"] == 1  # type: ignore[call-overload]
    assert row["first"] == 1.1  # type: ignore[call-overload]
    assert row["last"] == 1.111  # type: ignore[call-overload]
    assert row["priority"] == 100  # type: ignore[call-overload]
    assert row["host_in_downtime"] is False  # type: ignore[call-overload]
    assert row["contact_groups"] == ["some string1", "another string1"]  # type: ignore[call-overload]


def test_housekeeping(history_sqlite: SQLiteHistory) -> None:
    """Add 2 events to history, drop the older one."""

    event1 = ec.Event(host=HostName("ABC1"), text="Event1 text", core_host=HostName("ABC"))
    event2 = ec.Event(host=HostName("ABC2"), text="Event2 text", core_host=HostName("ABC"))
    history_sqlite.add(event=event1, what="NEW")
    history_sqlite.add(event=event2, what="NEW")

    with history_sqlite.conn as connection:
        cur = connection.cursor()
        cur.execute("SELECT count(*) FROM history;")
        assert cur.fetchone()["count(*)"] == 2

        cur.execute("UPDATE history set time = 123456 where host = 'ABC1'")
        history_sqlite.housekeeping()
        cur.execute("SELECT count(*) FROM history;")
        assert cur.fetchone()["count(*)"] == 1

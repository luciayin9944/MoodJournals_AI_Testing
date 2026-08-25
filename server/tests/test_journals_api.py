from datetime import timedelta


def test_retrieve_paginated_journal_history(
    client, auth_headers, make_entry, user_a, current_week_dates
):
    make_entry(user_a, current_week_dates[0])
    make_entry(user_a, current_week_dates[0] + timedelta(days=7))

    response = client.get("/journals?page=1", headers=auth_headers)

    assert response.status_code == 200
    body = response.get_json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert len(body["journals"]) == 2


def test_journal_history_is_isolated_by_user(
    client, auth_headers, make_entry, user_a, user_b, current_week_dates
):
    make_entry(user_a, current_week_dates[0])
    make_entry(user_b, current_week_dates[1])

    response = client.get("/journals", headers=auth_headers)

    assert response.status_code == 200
    body = response.get_json()
    assert body["total"] == 1
    assert body["journals"][0]["user"]["id"] == user_a.id


def test_weekly_entries_are_ordered_by_date(
    client, auth_headers, make_entry, user_a, current_week_dates
):
    later = make_entry(user_a, current_week_dates[3], notes="Later entry")
    earlier = make_entry(user_a, current_week_dates[0], notes="Earlier entry")
    iso_year, iso_week, _ = earlier.entry_date.isocalendar()

    response = client.get(
        f"/journals/{iso_year}/{iso_week}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.get_json()] == [earlier.id, later.id]

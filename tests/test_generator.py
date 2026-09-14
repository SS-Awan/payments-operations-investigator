from payops.generator import generate_world


def test_same_seed_produces_same_world():
    first = generate_world(seed=123)
    second = generate_world(seed=123)

    assert first == second


def test_every_attempt_belongs_to_a_payment():
    world = generate_world()

    payment_ids = {
        payment["payment_id"]
        for payment in world["payments"]
    }

    assert all(
        attempt["payment_id"] in payment_ids
        for attempt in world["payment_attempts"]
    )


def test_every_payment_has_at_least_one_attempt():
    world = generate_world()

    attempted_payment_ids = {
        attempt["payment_id"]
        for attempt in world["payment_attempts"]
    }

    assert all(
        payment["payment_id"] in attempted_payment_ids
        for payment in world["payments"]
    )


def test_successful_attempts_have_no_failure_code():
    world = generate_world()

    successful_attempts = [
        attempt
        for attempt in world["payment_attempts"]
        if attempt["status"] == "succeeded"
    ]

    assert all(
        attempt["failure_code"] is None
        for attempt in successful_attempts
    )


def test_failed_attempts_have_failure_code():
    world = generate_world()

    failed_attempts = [
        attempt
        for attempt in world["payment_attempts"]
        if attempt["status"] == "failed"
    ]

    assert all(
        attempt["failure_code"] is not None
        for attempt in failed_attempts
    )
def test_attempt_numbers_are_contiguous_per_payment():
    world = generate_world()

    for payment in world["payments"]:
        attempts = [
            attempt
            for attempt in world["payment_attempts"]
            if attempt["payment_id"] == payment["payment_id"]
        ]

        actual_numbers = [
            attempt["attempt_number"]
            for attempt in attempts
        ]

        assert actual_numbers == list(
            range(1, len(attempts) + 1)
        )


def test_no_attempts_occur_after_success():
    world = generate_world()

    for payment in world["payments"]:
        attempts = [
            attempt
            for attempt in world["payment_attempts"]
            if attempt["payment_id"] == payment["payment_id"]
        ]

        successful_positions = [
            index
            for index, attempt in enumerate(attempts)
            if attempt["status"] == "succeeded"
        ]

        if successful_positions:
            assert successful_positions == [len(attempts) - 1]
            assert payment["final_status"] == "succeeded"
        else:
            assert payment["final_status"] == "failed"
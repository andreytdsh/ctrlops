from ctrlops.services.log_service import analyze_log


def test_log_parsing(tmp_path):
    log = tmp_path / "access.log"
    log.write_text(
        "\n".join(
            [
                '127.0.0.1 - - [29/Jun/2026:10:00:01 +0000] "GET / HTTP/1.1" 200 123',
                '127.0.0.1 - - [29/Jun/2026:10:00:02 +0000] "GET /missing HTTP/1.1" 404 12',
                '10.0.0.2 - - [29/Jun/2026:10:01:02 +0000] "POST /api HTTP/1.1" 500 9',
            ]
        ),
        encoding="utf-8",
    )

    result = analyze_log(log)

    assert result["total_requests"] == 3
    assert result["count_404"] == 1
    assert result["count_500"] == 1
    assert result["status_distribution"] == {"200": 1, "404": 1, "500": 1}

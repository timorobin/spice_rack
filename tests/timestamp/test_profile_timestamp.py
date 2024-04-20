import datetime as dt
from spice_rack import ts_service, Logger


def profile(n: int):

    profiled_data = {}

    t0 = ts_service.Timestamp.now()
    for _ in range(n):
        dt.datetime.now()
    t1 = ts_service.Timestamp.now()
    profiled_data["dt_now"] = t1.seconds - t0.seconds

    t0 = ts_service.Timestamp.now()
    for _ in range(n):
        dt.datetime.utcnow()
    t1 = ts_service.Timestamp.now()
    profiled_data["dt_utc_now"] = t1.seconds - t0.seconds

    t0 = ts_service.Timestamp.now()
    for _ in range(n):
        ts_service.Timestamp.now()
    t1 = ts_service.Timestamp.now()
    profiled_data["ts_now"] = t1.seconds - t0.seconds

    t0 = ts_service.Timestamp.now()
    for _ in range(n):
        ts_service.Timestamp.utcnow()
    t1 = ts_service.Timestamp.now()
    profiled_data["ts_utc_now"] = t1.seconds - t0.seconds

    logger = Logger.get_logger()
    logger.info(
        "profiler results",
        [profiled_data]
    )


def test_profiler():
    profile(100)
    # raise ValueError("XXX")

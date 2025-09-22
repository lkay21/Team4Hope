def default_ndjson(model, category=None, net_score=None, net_score_latency=None, ramp_up_time=None, ramp_up_time_latency=None, bus_factor=None, bus_factor_latency=None,
    performance_claims=None, performance_claims_latency=None, license=None, license_latency=None, raspberry_pi=None, jetson_nano=None, desktop_pc=None, aws_server=None, size_score_latency=None, dataset_and_code_score=None, dataset_and_code_score_latency=None,
    dataset_quality=None, dataset_quality_latency=None, code_quality=None,code_quality_latency=None):
    
    if category is not None:
        name = model.rstrip('/').split('/')[-1]
    else:
        name = None

    def score(val):
        return float(val) if val is not None else 0.0
    def latency(val):
        return int(val) if val is not None else 0

    ndjson = {
        "name": name,
        "category": category,
        "net_score": score(net_score),
            "net_score_latency": latency(net_score_latency),
            "ramp_up_time": score(ramp_up_time),
            "ramp_up_time_latency": latency(ramp_up_time_latency),
            "bus_factor": score(bus_factor),
            "bus_factor_latency": latency(bus_factor_latency),
            "performance_claims": score(performance_claims),
            "performance_claims_latency": latency(performance_claims_latency),
            "license": score(license),
            "license_latency": latency(license_latency),
            "size_score": {
                "raspberry_pi": score(raspberry_pi),
                "jetson_nano": score(jetson_nano),
                "desktop_pc": score(desktop_pc),
                "aws_server": score(aws_server)
            },
            "size_score_latency": latency(size_score_latency),
            "dataset_and_code_score": score(dataset_and_code_score),
            "dataset_and_code_score_latency": latency(dataset_and_code_score_latency),
            "dataset_quality": score(dataset_quality),
            "dataset_quality_latency": latency(dataset_quality_latency),
            "code_quality": score(code_quality),
            "code_quality_latency": latency(code_quality_latency)
        }

    return ndjson

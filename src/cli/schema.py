def default_ndjson(url, category=None, net_score=None, net_score_latency=None, ramp_up_time=None, ramp_up_time_latency=None, bus_factor=None, bus_factor_latency=None,
    performance_claims=None, performance_claims_latency=None, license=None, license_latency=None, raspberry_pi=None, jetson_nano=None, desktop_pc=None, aws_server=None, size_score_latency=None, dataset_and_code_score=None, dataset_and_code_score_latency=None,
    dataset_quality=None, dataset_quality_latency=None, code_quality=None,code_quality_latency=None):

    if category is not None:
        name = url.rstrip('/').split('/')[-1]
    else:
        name = None

    ndsjon = {
        "name": name, "category": category, "net_score": net_score, "net_score_latency": net_score_latency, "ramp_up_time": ramp_up_time,
        "ramp_up_time_latency": ramp_up_time_latency, "bus_factor": bus_factor, "bus_factor_latency": bus_factor_latency,"performance_claims": performance_claims,
        "performance_claims_latency": performance_claims_latency, "license": license, "license_latency": license_latency,
        "size_score": {"raspberry_pi": raspberry_pi, "jetson_nano": jetson_nano, "desktop_pc": desktop_pc, "aws_server": aws_server},
        "size_score_latency": size_score_latency, "dataset_and_code_score": dataset_and_code_score, "dataset_and_code_score_latency": dataset_and_code_score_latency,
        "dataset_quality": dataset_quality, "dataset_quality_latency": dataset_quality_latency, "code_quality": code_quality, "code_quality_latency": code_quality_latency
    }
    
    return ndsjon

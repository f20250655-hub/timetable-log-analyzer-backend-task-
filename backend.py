def parse_logs(filename):
    total_requests = 0
    endpoints = {}
    statuses = {}
    users_by_year = {}   # batch-wise unique IDs
    timetable_hits = 0
    endpoint_times = {}
    algo_count = {}

    with open(filename, "r") as f:
        for line in f:
            parts = line.split()
            if "GET" in line or "POST" in line:
                total_requests += 1

                # figure out method
                method = "GET" if "GET" in line else "POST"

                # try to pull out endpoint and status
                try:
                    endpoint = parts[parts.index(method) + 1]
                    status = parts[parts.index(method) + 2]
                except Exception:
                    endpoint, status = "?", "000"
                endpoints[endpoint] = endpoints.get(endpoint, 0) + 1
                statuses[status] = statuses.get(status, 0) + 1
                if "/generate" in endpoint:
                    timetable_hits += 1

                # response time capture
                if "ms" in line or "µs" in line:
                    for elem in parts:
                        if "ms" in elem or "µs" in elem:
                            val = elem.replace("ms", "").replace("µs", "")
                            try:
                                val = float(val)
                                if "µs" in elem:   # convert microseconds
                                    val /= 1000.0
                                endpoint_times.setdefault(endpoint, []).append(val)
                            except ValueError:
                                continue

            # user IDs
            for elem in parts:
                if elem.startswith("[") and elem.endswith("]") and len(elem) > 5:
                    uid = elem.strip("[]")
                    yr = uid[:4]
                    if yr.isdigit():
                        users_by_year.setdefault(yr, set()).add(uid)

            # algorithm 
            if "Backtracking" in line:
                algo_count["Backtracking"] = algo_count.get("Backtracking", 0) + 1
            if "Iterative" in line:
                algo_count["Iterative"] = algo_count.get("Iterative", 0) + 1

    # build report
    out = []
    out.append("Traffic & Usage Analysis")
    out.append("-------------------------")
    out.append(f"Total API Requests: {total_requests}\n")

    out.append("Endpoint Popularity:")
    for ep, c in sorted(endpoints.items(), key=lambda x: x[1], reverse=True):
        pct = (c / total_requests * 100) if total_requests else 0
        if pct >= 0.1:   # ignore <0.1%
            out.append(f"- {ep}: {c} requests ({pct:.1f}%)")

    out.append("\nHTTP Status Codes:")
    for st, c in statuses.items():
        out.append(f"- {st}: {c} times")

    out.append("\nPerformance Metrics")
    out.append("-------------------")
    for ep, times in endpoint_times.items():
        if times:
            avg = sum(times) / len(times)
            mx = max(times)
            out.append(f"Endpoint: {ep}")
            out.append(f"  Avg Response: {avg:.2f} ms")
            out.append(f"  Max Response: {mx:.2f} ms")

    out.append("\nApplication Insights")
    out.append("--------------------")
    for a, c in algo_count.items():
        out.append(f"{a}: {c} times")

    # timetables
    gen_calls = endpoints.get("/generate", 0)
    avg_tt = (timetable_hits / gen_calls) if gen_calls else 0
    out.append(f"Average Timetables per /generate: {avg_tt:.2f}")
    out.append(f"Total Timetables: {timetable_hits}")

    # unique IDs
    out.append("\nUnique ID Analysis")
    out.append("------------------")
    total_unique = sum(len(s) for s in users_by_year.values())
    out.append(f"Total Unique IDs: {total_unique}")
    for y, ids in sorted(users_by_year.items()):
        out.append(f"Batch {y}: {len(ids)} unique IDs")

    return "\n".join(out)


if __name__ == "__main__":
    path = "/Users/architagarwal2007/Documents/coding/python/1.log"
    print(parse_logs(path))

import re
from collections import defaultdict

def parse_logs(filename):
    total_requests = 0
    endpoint_counts = defaultdict(int)
    status_counts = defaultdict(int)
    user_ids = set()
    user_years = defaultdict(int)
    timetable_count = 0
    endpoint_times = defaultdict(list)
    algorithms = defaultdict(int)

    # Patterns
    req_pattern = re.compile(r'(GET|POST) (.*?) (\d{3})')
    user_pattern = re.compile(r'\[(\d{4}[A-Z0-9]+)\]')
    time_pattern = re.compile(r'(\d+\.\d+)(µs|ms)')
    algo_pattern = re.compile(r'(Backtracking|Iterative)', re.IGNORECASE)

    with open(filename, "r") as f:
        for line in f:
            # Requests
            req = req_pattern.search(line)
            if req:
                total_requests += 1
                _, endpoint, status = req.groups()
                endpoint_counts[endpoint] += 1
                status_counts[status] += 1

                # Response time
                t = time_pattern.search(line)
                if t:
                    val, unit = t.groups()
                    val = float(val)
                    ms = val/1000 if unit == "µs" else val
                    endpoint_times[endpoint].append(ms)

                # Count timetables
                timetable_count += 1  

            # Users
            u = user_pattern.search(line)
            if u:
                uid = u.group(1)
                user_ids.add(uid)
                year = uid[:4]
                user_years[year] += 1

            # Algorithms
            a = algo_pattern.search(line)
            if a:
                algorithms[a.group(1).capitalize()] += 1

    # Report
    report = []
    report.append("Traffic & Usage Analysis")
    report.append("-------------------------")
    report.append(f"Total API Requests: {total_requests}\n")

    report.append("Endpoint Popularity:")
    for ep, count in endpoint_counts.items():
        pct = (count / total_requests * 100) if total_requests else 0
        report.append(f"- {ep}: {count} requests ({pct:.1f}%)")

    report.append("\nHTTP Status Codes:")
    for code, count in status_counts.items():
        report.append(f"- {code}: {count} times")

    report.append("\nPerformance Metrics")
    report.append("-------------------")
    for ep, times in endpoint_times.items():
        if times:
            avg_t = sum(times) / len(times)
            max_t = max(times)
            report.append(f"Endpoint: {ep}")
            report.append(f"  Avg Response: {avg_t:.2f} ms")
            report.append(f"  Max Response: {max_t:.2f} ms")

    report.append("\nApplication Insights")
    report.append("--------------------")
    for algo, count in algorithms.items():
        report.append(f"{algo}: {count} times")

    if endpoint_counts["/generate"]:
        avg_tt = timetable_count / endpoint_counts["/generate"]
    else:
        avg_tt = 0
    report.append(f"Average Timetables per /generate: {avg_tt:.2f}")
    report.append(f"Total Timetables: {timetable_count}")

    report.append("\nUnique ID Analysis")
    report.append("------------------")
    report.append(f"Total Unique IDs: {len(user_ids)}")
    for year, count in sorted(user_years.items()):
        report.append(f"Batch {year}: {count} unique IDs")

    return "\n".join(report)


if __name__ == "__main__":
    filename = "/Users/architagarwal2007/Documents/coding/python/1.log"   # just put your file in same folder
    print(parse_logs(filename))

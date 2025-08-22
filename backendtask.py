import re
from collections import defaultdict
import os
import sys

def parse_logs(filename):
    total_requests = 0
    endpoint_counts = defaultdict(int)
    status_counts = defaultdict(int)
    user_ids = set()
    user_years = defaultdict(int)
    timetable_count = 0
    endpoint_times = defaultdict(list)
    algorithms = defaultdict(int)

    # Regex patterns
    request_pattern = re.compile(r'(GET|POST) (.*?) (\d{3})')
    user_pattern = re.compile(r'\[(\d{4}[A-Z0-9]+)\]') 
    time_pattern = re.compile(r'(\d+\.\d+)(µs|ms)')     
    algo_pattern = re.compile(r'\b(Backtracking|Iterative)\b', re.IGNORECASE)

    with open(filename, "r") as f:
        for line in f:
            # API requests + status
            match = request_pattern.search(line)
            if match:
                total_requests += 1
                method, endpoint, status = match.groups()
                endpoint_counts[endpoint] += 1
                status_counts[status] += 1

                # Response times
                t = time_pattern.search(line)
                if t:
                    value, unit = t.groups()
                    value = float(value)
                    response_time_ms = value / 1000 if unit == "µs" else value
                    endpoint_times[endpoint].append(response_time_ms)

                timetable_count += 1  

            # Users
            u = user_pattern.search(line)
            if u:
                uid = u.group(1)
                user_ids.add(uid)
                year = uid[:4]
                user_years[year] += 1

            # Algorithms
            algo = algo_pattern.search(line)
            if algo:
                algo_name = algo.group(1).capitalize()
                algorithms[algo_name] += 1

    # --- Report ---
    report = []
    report.append("📊 Traffic & Usage Analysis")
    report.append("-----------------------------------")
    report.append(f"Total API Requests Logged: {total_requests}\n")

    report.append("Endpoint Popularity:")
    for ep, count in endpoint_counts.items():
        percent = (count / total_requests * 100) if total_requests else 0
        report.append(f"  - {ep}: {count} requests ({percent:.1f}%)")

    report.append("\nHTTP Status Codes:")
    for code, count in status_counts.items():
        report.append(f"  - {code}: {count} times")

    report.append("-----------------------------------")
    report.append("🚀 Performance Metrics")
    report.append("-----------------------------------")
    for ep, times in endpoint_times.items():
        if times:
            avg_time = sum(times) / len(times)
            max_time = max(times)
            report.append(f"Endpoint: {ep}")
            report.append(f"  - Average Response Time: {avg_time:.2f} ms")
            report.append(f"  - Max Response Time: {max_time:.2f} ms")

    report.append("\n⚙️ Application-Specific Insights")
    report.append("-----------------------------------")
    if algorithms:
        report.append("Timetable Generation Strategy Usage:")
        for algo, count in algorithms.items():
            report.append(f"  - {algo}: {count} times")

    report.append(f"\nAverage Timetables Found per /generate call: {timetable_count/ (endpoint_counts['/generate'] or 1):.2f}")
    report.append(f"Total number of timetables generated: {timetable_count}")

    report.append("-----------------------------------")
    report.append("🧑‍🤝‍🧑 Unique ID Analysis")
    report.append("-----------------------------------")
    report.append(f"Total Unique IDs found: {len(user_ids)}")
    for year, count in sorted(user_years.items()):
        report.append(f"Batch of {year}: {count} unique IDs")

    return "\n".join(report)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if not os.path.isabs(filename):
            filename = os.path.join(script_dir, filename)
    else:
        filename = os.path.join(script_dir, "1.log")

    print(f"Looking for log file at: {filename}\n")
    print(parse_logs(filename))


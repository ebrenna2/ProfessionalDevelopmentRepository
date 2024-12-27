
import requests
from flask import Flask, render_template_string, request
import re
from bs4 import BeautifulSoup
import json
app = Flask(__name__)

def remove_exact_duplicate(s):
    s = s.strip()
    n = len(s)
    if n % 2 == 0:
        half = n // 2
        if s[:half] == s[half:]:
            return s[:half]
    return s

urls = [
    "https://www.nfl.com/stats/team-stats/offense/rushing/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/offense/receiving/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/offense/scoring/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/offense/downs/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/defense/passing/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/defense/rushing/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/defense/receiving/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/defense/scoring/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/defense/tackles/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/defense/downs/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/defense/fumbles/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/defense/interceptions/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/special-teams/field-goals/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/special-teams/scoring/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/special-teams/kickoffs/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/special-teams/kickoff-returns/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/special-teams/punts/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/special-teams/punt-returns/2024/reg/all",
    "https://www.nfl.com/stats/team-stats/offense/rushing/2022/reg/all",
    "https://www.nfl.com/stats/team-stats/offense/receiving/2022/reg/all",
    "https://www.nfl.com/stats/team-stats/offense/scoring/2022/reg/all",
    "https://www.nfl.com/stats/team-stats/offense/downs/2022/reg/all",
    "https://www.nfl.com/stats/team-stats/defense/passing/2022/reg/all",
    "https://www.nfl.com/stats/team-stats/defense/rushing/2022/reg/all",
    "https://www.nfl.com/stats/team-stats/defense/receiving/2022/reg/all",
    "https://www.nfl.com/stats/team-stats/defense/scoring/2022/reg/all",
    "https://www.nfl.com/stats/team-stats/defense/tackles/2022/reg/all",
    "https://www.nfl.com/stats/team-stats/defense/downs/2022/reg/all",
    "https://www.nfl.com/stats/team-stats/defense/fumbles/2022/reg/all",
    "https://www.nfl.com/stats/team-stats/defense/interceptions/2022/reg/all",
    "https://www.nfl.com/stats/team-stats/special-teams/field-goals/2022/reg/all",
    "https://www.nfl.com/stats/team-stats/special-teams/scoring/2022/reg/all",
    "https://www.nfl.com/stats/team-stats/special-teams/kickoffs/2022/reg/all",
    "https://www.nfl.com/stats/team-stats/special-teams/kickoff-returns/2022/reg/all",
    "https://www.nfl.com/stats/team-stats/special-teams/punts/2022/reg/all",
    "https://www.nfl.com/stats/team-stats/special-teams/punt-returns/2022/reg/all"
]

output_file = "nfl_stats_no_repeats.txt"


def scrape_nfl_stats():
    all_rows = []

    with open(output_file, "w", encoding="utf-8") as f:
        for url in urls:
            match = re.search(r"/(\d{4})/", url)
            year = match.group(1) if match else "Unknown Year"

            all_rows.append(["Year:", year, "URL:", url])
            all_rows.append([("=" * 80), "", ""])  # Separator

            r = requests.get(url)
            soup = BeautifulSoup(r.content, "html.parser")
            table = soup.find("table", class_="d3-l-grid--inner")

            if not table:
                f.write("No table with class 'd3-l-grid--inner' found. Showing all <tr>...\n\n")
                all_rows.append(["No table found"])
                rows = soup.find_all("tr")
            else:
                rows = table.find_all("tr")

            for row in rows:
                ths = [th.get_text(strip=True) for th in row.find_all("th")]
                tds = [remove_exact_duplicate(td.get_text(strip=True)) for td in row.find_all("td")]


                if ths:
                    f.write(f"TR (headers) [{year}]: " + " | ".join(ths) + "\n")
                    all_rows.append([year] + ths)
                elif tds:
                    f.write(f"TD (data) [{year}]: " + " | ".join(tds) + "\n")
                    all_rows.append([year] + tds)

            f.write("\n\n")

    print(f"Done! Check '{output_file}' for results without repeated team names.")
    return all_rows
scraped_data_cache = None

@app.route("/", methods=["GET", "POST"])
def index():
    global scraped_data_cache
    if not scraped_data_cache:
        scraped_data_cache = scrape_nfl_stats()
    query = request.args.get("search", "").lower()
    filtered_data = scraped_data_cache

    if query:
        filtered_data = [
            row for row in scraped_data_cache
            if any(query in str(cell).lower() for cell in row)
        ]

    table_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NFL Stats</title>
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.1/css/jquery.dataTables.min.css">
        <style>
            body { font-family: Arial, sans-serif; margin: 2em; }
            a { color: #0066cc; }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-top: 1em;
            }
            th, td {
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
            }
            tr:nth-child(even) { background-color: #f9f9f9; }
        </style>
    </head>
    <body>
        <h1>NFL Stats (Scraped Data)</h1>
        <p><a href="/refresh">Refresh / Re-scrape</a></p>

<form method="get" action="/">
    <input type="text" name="search" placeholder="Search..." value="{{ request.args.get('search', '') }}">
    <button type="submit">Filter</button>
</form>

        <table id="nfl-stats" class="display">
            <thead>
                <tr>
                    {% for cell in data[0] %}
                      <th>{{ cell }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in data[1:] %}
                  <tr>
                    {% for cell in row %}
                      <td>{{ cell }}</td>
                    {% endfor %}
                  </tr>
                {% endfor %}
            </tbody>
        </table>

        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.1/js/jquery.dataTables.min.js"></script>
        <script>
            $(document).ready(function() {
                $('#nfl-stats').DataTable({
                    "paging": true,
                    "searching": true,
                    "ordering": true
                });
            });
        </script>
    </body>
    </html>
    """

    return render_template_string(table_template, data=filtered_data)

@app.route("/refresh")
def refresh():
    global scraped_data_cache
    scraped_data_cache = scrape_nfl_stats()
    return (
        "Refreshed and re-scraped data! "
        "<br><br>"
        "<a href='/'>Go Back to Home</a>"
    )

if __name__ == "__main__":
    app.run(debug=True)

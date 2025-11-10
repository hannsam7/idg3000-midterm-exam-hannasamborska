import os
import json
import glob
import csv

base_dir = os.path.dirname(__file__)
lighthouse_dir = os.path.join(base_dir, '..', 'evidence', 'lighthouse')
hosting_dir = os.path.join(base_dir, '..', 'evidence', 'hosting')
output_csv = os.path.join(base_dir, '..', 'evidence', 'results.csv')

fieldnames = ['Municipality', 'URL', 'PerfScore', 'FCP', 'LCP', 'SpeedIndex', 'GreenHosting', 'CarbonTxt']

def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for path in sorted(glob.glob(os.path.join(lighthouse_dir, '*.json'))):
        data = read_json(path)
        domain = os.path.splitext(os.path.basename(path))[0]

        url = data.get('requestedUrl', '')
        audits = data.get('audits', {})
        perf_score = data.get('categories', {}).get('performance', {}).get('score', None)
        perf_score_pct = round(perf_score * 100) if isinstance(perf_score, (int, float)) else ''

        fcp = audits.get('first-contentful-paint', {}).get('numericValue', '')
        lcp = audits.get('largest-contentful-paint', {}).get('numericValue', '')
        speed = audits.get('speed-index', {}).get('numericValue', '')

        # Green hosting status
        green_path = os.path.join(hosting_dir, f'{domain}_greenweb.json')
        if os.path.exists(green_path):
            green_json = read_json(green_path)
            green_hosting = 'Yes' if green_json.get('green') is True else 'No'
        else:
            green_hosting = ''

        # carbon.txt presence
        carbon_path = os.path.join(hosting_dir, f'{domain}_carbon.txt')
        carbon_txt = 'Yes' if os.path.exists(carbon_path) else 'No'

        writer.writerow({
            'Municipality': domain,
            'URL': url,
            'PerfScore': perf_score_pct,
            'FCP': fcp,
            'LCP': lcp,
            'SpeedIndex': speed,
            'GreenHosting': green_hosting,
            'CarbonTxt': carbon_txt
        })

print(f'Wrote CSV: {output_csv}')
import os
import json
import glob
import csv

base_dir = os.path.dirname(__file__)
lighthouse_dir = os.path.join(base_dir, '..', 'evidence', 'lighthouse')
hosting_dir = os.path.join(base_dir, '..', 'evidence', 'hosting')
output_csv = os.path.join(base_dir, '..', 'evidence', 'results.csv')

fieldnames = ['Municipality','URL','PerfScore','FCP','LCP','SpeedIndex','PageWeightBytes','Requests','GreenHosting','CarbonTxt','CO2_SWD_g','CO2_OneByte_g']

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
        page_bytes = audits.get('total-byte-weight', {}).get('numericValue', '')
        req_items = audits.get('network-requests', {}).get('details', {}).get('items', []) if audits.get('network-requests') else []
        req_count = len(req_items) if isinstance(req_items, list) else ''

                # Green hosting
        green_path = os.path.join(hosting_dir, f'{domain}_greenweb.json')
        if os.path.exists(green_path):
            green_json = read_json(green_path)
            green_hosting = 'Yes' if green_json.get('green') is True else 'No'
        else:
            green_hosting = ''

        # carbon.txt
        carbon_path = os.path.join(hosting_dir, f'{domain}_carbon.txt')
        carbon_txt = 'Yes' if os.path.exists(carbon_path) else 'No'

        # CO2 (from compute_co2.js output)
        co2_path = os.path.join(hosting_dir, f'{domain}_co2.json')
        co2_swd = ''
        co2_onebyte = ''
        if os.path.exists(co2_path):
            co2_json = read_json(co2_path)
            co2_swd = co2_json.get('co2_swd_g', '')
            co2_onebyte = co2_json.get('co2_onebyte_g', '')

        writer.writerow({
            'Municipality': domain,
            'URL': url,
            'PerfScore': perf_score_pct,
            'FCP': fcp,
            'LCP': lcp,
            'SpeedIndex': speed,
            'PageWeightBytes': page_bytes,
            'Requests': req_count,
            'GreenHosting': green_hosting,
            'CarbonTxt': carbon_txt,
            'CO2_SWD_g': co2_swd,
            'CO2_OneByte_g': co2_onebyte
        })

print(f'Wrote CSV: {output_csv}')
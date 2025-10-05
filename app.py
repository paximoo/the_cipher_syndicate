import csv
from statistics import mean
from flask import Flask, render_template, request, send_file
from requests import get as req_get

app = Flask(__name__, template_folder='static//templates')
DATA = {}
PARAM_ENTRIES = []
PARAMETERS = ['T2M', 'T2M_MAX', 'T2M_MIN', 'PRECTOTCORR', 'WD10M', 'WS10M', 'PS', 'QV2M']
LAT, LONG = None, None
START_YEAR, END_YEAR = 1990, 2025

@app.route('/', methods=['POST', 'GET'])
def index():
  if request.method == 'POST':
    LAT, LONG, date = request.form.get('latitude'), float(request.form.get('longitude'))%360, request.form.get('date')
    RESPONSE = req_get(
      'https://power.larc.nasa.gov/api/temporal/daily/point' +
      f'?parameters={','.join(PARAMETERS)}&community=RE&latitude={LAT}&longitude={LONG if LONG <= 180 else 360-LONG}&start={START_YEAR}0101&end={END_YEAR}0101&format=JSON'
    ).json()

    RESPONSE = RESPONSE['properties']['parameter']

    DATA = {}
    for param, recs in RESPONSE.items():
      DATA[param] = {}
      for day, value in recs.items():
        if day[4:] == date.replace('-','')[4:]:
          DATA[param][day] = value

    for i in range(len(PARAMETERS)):
      PARAM_ENTRIES.append([])

    for index, (param, vals) in enumerate(list(DATA.items())):
      for _, value in enumerate(list(vals.items())):
        PARAM_ENTRIES[index] += [value[1]]

    param_avg = [f"{mean(e):.2f}" for e in PARAM_ENTRIES]
    
    return render_template('results.html',
      param_entries=PARAM_ENTRIES,
      params=PARAMETERS,
      param_num=len(PARAMETERS),
      avgs=param_avg,
      date=date,
      lat=LAT,
      long=LONG,
      start_year=START_YEAR
    )

  else:
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
  with open('out.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['Year'] + PARAMETERS)
    writer.writeheader()
    for rec_ind in range(len(PARAM_ENTRIES[0])):
      row = {'Year': START_YEAR + rec_ind}
      for par_ind, param in enumerate(PARAMETERS):
        row[param] = PARAM_ENTRIES[par_ind][rec_ind]

      writer.writerow(row)

  return send_file('out.csv', as_attachment=True)

@app.route('/graph', methods=['POST'])
def graph():
  param = request.form.get('parameter')
  lat, long = request.form.get('lat'), request.form.get('long')
  return req_get(
    'https://power.larc.nasa.gov/api/toolkit/power/visualizations/heatmaps?operation=climatological-days' +
    f'&start=1990-01-01T00%3A00%3A00&end=2024-01-01T00%3A00%3A00&latitude={lat}&longitude={long}&community=ag&parameter={param}&format=html&units=metric'
  ).text

@app.route('/about-us')
def about_us():
  return render_template('about-us.html')


if __name__ == '__main__':
  app.run(port=8080, host='127.0.0.5', debug=True)

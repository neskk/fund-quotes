
var timeFormat = 'DD/MM/YYYY HH:mm';
/*
function newDate(days) {
  return moment().add(days, 'd').toDate();
}

function newDateString(days) {
  return moment().add(days, 'd').format(timeFormat);
}
*/

var lineChartData = {
  datasets: [
  {
    label: "Humidity",
    yAxisID: 'y-axis-h',
    borderColor: "rgba(151,187,205,0.8)",
    backgroundColor: "rgba(151,187,205,0.75)",
    fill: false,
    data: [],
  },
  {
    label: "Temperature",
    yAxisID: 'y-axis-t',
    borderColor: "rgba(255,86,86,0.8)",
    backgroundColor: "rgba(255,86,86,0.75)",
    fill: false,
    data: [],
  }]
};

var datasetHumidity = {
  label: "Humidity",
  yAxisID: 'y-axis-h',
  borderColor: "rgba(151,187,205,0.8)",
  backgroundColor: "rgba(151,187,205,0.75)",
  fill: false,
  lineTension: 0,
  borderWidth: 2,
  pointRadius: 0,
  data: [],
};


var datasetTemperature = {
  label: "Temperature",
  yAxisID: 'y-axis-t',
  borderColor: "rgba(255,86,86,0.8)",
  backgroundColor: "rgba(255,86,86,0.75)",
  fill: false,
  lineTension: 0,
  borderWidth: 2,
  pointRadius: 0,
  data: [],
};

var temperature_data = [];
var humidity_data = [];

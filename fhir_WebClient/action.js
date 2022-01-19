Vue.use(VueResource);
const app = new Vue({
  el: "#app",
  data: {
    isClick: false,
    hasData: false,
    model: "",
    param_id: "test-03121002",
    param_hour: 24,
    predict_value: 0.0,
    // qcsi_value: {
    //     "fio2": {
    //         "date": "",
    //         "value": 0
    //     },
    //     "respiratory rate": {
    //         "date": "",
    //         "value": 0
    //     },
    //     "spo2": {
    //         "date": "",
    //         "value": 0
    //     }
    // },
    results: {
        "fio2": {
          "date": "1990-01-01",
          "value": 0
        },
        "respiratory rate": {
          "date": "1990-01-01",
          "value": 0
        },
        "spo2": {
          "date": "1990-01-01",
          "value": 0
        },
        "pulse oximetry":{
          "date": "1990-01-01",
          "value": 0
        },
        "o2 flow rate":{
          "date": "1990-01-01",
          "value": 0
        },
    },
  },
  methods: {
    searchQuery: () => {
      app.isClick = true;
      app.$http
        .get(`http://localhost:5000/${app.model}`, {
          params: { id: app.param_id, hourAliveTime: app.param_hour },
        })
        .then(
          (response) => {
            app.hasData = true;
            result_json = response.data;
            //callback successed
            if (result_json.hasOwnProperty("predict_value")) {
              app.predict_value = result_json.predict_value;
              delete result_json["predict_value"];
            }
            app.results = result_json;
          },
          (response) => {
            //callback errored
            app.hasData = false;
          }
        );
    },
    textchange: () => {
      app.result_changes();
    },
    radioclicks: (key, value) => {
      app.results[key].value = value;
      app.result_changes();
    },
    result_changes: () => {
      app.$http
        .post(`http://localhost:5000/${app.model}/change`, app.results, {})
        .then(
          (response) => {
            app.predict_value = response.data.predict_value;
          },
          () => {
            console.log("Change failed");
          }
        );
    },
  },
});

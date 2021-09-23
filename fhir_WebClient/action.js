Vue.use(VueResource)
const app = new Vue({
    el: "#app",
    data: {
        isClick: false,
        hasData: false,
        model: "",
        param_id: "test-03121002",
        predict_value: 0.00,
        qcsi_value: {
            "fio2": {
                "date": "", 
                "value": 0
            }, 
            "respiratory rate": {
                "date": "", 
                "value": 0
            }, 
            "spo2": {
                "date": "", 
                "value": 0
            }
        },
        results: {}
    },
    methods: {
        searchQuery: () => {
            app.$http.get(`http://localhost:5000/${app.model}`, { params: { id: app.param_id } }).then(response => {
                app.hasData = true
                //callback successed
                result_json = response.data
                if (app.model == "qcsi")
                    app.qcsiSearchQuery(result_json)
                else if (app.model == "rox")
                    app.roxSearchQuery(result_json)
                else {
                    if (result_json.hasOwnProperty("predict_value")) {
                        app.predict_value = response.data.predict_value
                        delete result_json["predict_value"]
                    }
                    app.results = result_json
                }
            }, response => {
                //callback errored
                app.hasData = false
            }).then(() => {
                app.isClick = true
            })
        },
        qcsiSearchQuery: (results) => {
            for (let key in results) {
                switch (key) {
                    case 'fio2':
                        if (results[key].value <= 2)
                            results[key].value = 0
                        else if (results[key].value >= 5)
                            results[key].value = 5
                        else
                            results[key].value = 4
                        break;
                    case 'respiratory rate':
                        if (results[key].value <= 22)
                            results[key].value = 0
                        else if (results[key].value >= 28)
                            results[key].value = 2
                        else
                            results[key].value = 1
                        break
                    case 'spo2':
                        if (results[key].value > 92)
                            results[key].value = 0
                        else if (results[key].value <= 88)
                            results[key].value = 5
                        else
                            results[key].value = 2
                        
                }
            }
            app.qcsi_value = results
        },
        radio_qcsi_rox_clicks: (type, key, value) => {
            if (type === 'qcsi')
                app.qcsi_value[key].value = value
        },
        roxSearchQuery: (results) => {

        },
        
        radioclicks: (key, bool) => {
            app.results[key].value = bool
        }
    }
})

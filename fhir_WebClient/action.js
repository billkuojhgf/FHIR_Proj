Vue.use(VueResource)
const app = new Vue({
    el: "#app",
    data: {
        isClick: false,
        hasData: false,
        model: "",
        param_id: "test-03121002",
        predict_value: 0.00,
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
        results: {}
    },
    methods: {
        searchQuery: () => {
            app.$http.get(`http://localhost:5000/${app.model}`, { params: { id: app.param_id } }).then(response => {
                app.hasData = true
                result_json = response.data
                //callback successed
                if (result_json.hasOwnProperty("predict_value")) {
                    app.predict_value = response.data.predict_value
                    delete result_json["predict_value"]
                }
                app.results = result_json
                
            }, response => {
                //callback errored
                app.hasData = false
            }).then(() => {
                app.isClick = true
            })
        },
        textchange: () => {
            console.log("textchange")
        },
        radioclicks: (key, value) => {
            app.results[key].value = value
        }
    }
})

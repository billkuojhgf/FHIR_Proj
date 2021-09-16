Vue.use(VueResource)
const app = new Vue({
    el: "#app",
    data: {
        showTab:[false, false],
        isClick: false,
        hasData: false,
        model: "",
        param_id: "test-03121002",
        predict_value: 0.00,
        results: {}
    },
    methods: {
        searchQuery: () => {
            app.$http.get(`http://localhost:5000/${app.model}`, { params: { id: app.param_id } }).then(response => {
                app.hasData = true
                //callback successed
                result_json = response.data
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
        radioclicks: (key, bool) => {
            app.results[key].value = bool
        },
        tabClicks: (key) => {
            for (i = 0; i < app.showTab.length; i++) {
                app.showTab[i] = false
            }
            app.showTab[key] = true
        }
    }
})

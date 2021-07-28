Vue.use(VueResource)
const app = new Vue({
    el: "#app",
    data: {
        isClick: false,
        hasData: false,
        model: "diabetes",
        param_id: "",
        predict_value: 0.00,
        results: {}
    },
    methods: {
        searchQuery: () => {
            app.isClick = true
            app.$http.get(`http://localhost:5000/${app.model}`, { params: { id: app.param_id } }).then(response => {
                //callback sucessed
                app.hasData = true
                result_json = response.data
                app.predict_value = response.data.predict_value
                delete result_json["predict_value"]
                app.results = result_json
            }, response => {
                //callback errored
                app.hasData = false
            })
        }
    }
})
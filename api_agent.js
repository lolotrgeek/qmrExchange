const http = require('http')

const base = 'http://localhost:5000/api/v1'


// make get request to api
function make_request(url) {
    http.get(url, response => {
        let body = ''
        response.on('data', data => {
            body += data.toString()
        })

        response.on('end', () => {
            const profile = JSON.parse(body)
            console.log(url, profile)
        })
    }
    )
}


function get_latest_trade(ticker='XYZ') {
    const url =  `${base}/get_latest_trade?ticker=${ticker}`
    make_request(url)
}

function get_best_bid(ticker='XYZ') {
    const url =  `${base}/get_best_bid?ticker=${ticker}`
    make_request(url)
}

function get_best_ask(ticker='XYZ') {
    const url =  `${base}/get_best_ask?ticker=${ticker}`
    make_request(url)
}

function get_midprice(ticker='XYZ') {
    const url =  `${base}/get_midprice?ticker=${ticker}`
    make_request(url)
}

function get_order_book(ticker='XYZ') {
    const url =  `${base}/get_order_book?ticker=${ticker}`
    make_request(url)
}

function get_quotes(ticker='XYZ') {
    const url =  `${base}/get_quotes?ticker=${ticker}`
    make_request(url)
}

function get_trades(ticker='XYZ') {
    const url =  `${base}/get_trades?ticker=${ticker}`
    make_request(url)
}


get_latest_trade()
get_best_bid()
get_best_ask()
get_midprice()
get_order_book()
get_quotes()
get_trades()
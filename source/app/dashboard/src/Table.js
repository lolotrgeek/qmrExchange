import React, { useEffect, useState } from 'react'

const base_url = 'http://127.0.0.1:5000'

const TableComponent = ({ ticker }) => {
    const [candles, setCandles] = useState([])
    const [orderBook, setOrderBook] = useState({bids:[], asks:[]})
    const [trades, setTrades] = useState([])
    const [quotes, setQuotes] = useState({})
    const [bestBid, setBestBid] = useState({})
    const [bestAsk, setBestAsk] = useState({})
    const [midprice, setMidprice] = useState('')

    useEffect(() => {
        const fetchData = async () => {
            const candleResponse = await fetch(`${base_url}/api/v1/candles?ticker=${ticker}`)
            const candleData = await candleResponse.json()
            console.log(candleData)
            setCandles(candleData)

            const orderBookResponse = await fetch(`${base_url}/api/v1/get_order_book?ticker=${ticker}`)
            const orderBookData = await orderBookResponse.json()
            setOrderBook(orderBookData)

            const tradesResponse = await fetch(`${base_url}/api/v1/get_trades?ticker=${ticker}`)
            const tradesData = await tradesResponse.json()
            setTrades(tradesData)

            const quotesResponse = await fetch(`${base_url}/api/v1/get_quotes?ticker=${ticker}`)
            const quotesData = await quotesResponse.json()
            setQuotes(quotesData)

            const bestBidResponse = await fetch(`${base_url}/api/v1/get_best_bid?ticker=${ticker}`)
            const bestBidData = await bestBidResponse.json()
            setBestBid(bestBidData)

            const bestAskResponse = await fetch(`${base_url}/api/v1/get_best_ask?ticker=${ticker}`)
            const bestAskData = await bestAskResponse.json()
            setBestAsk(bestAskData)

            const midpriceResponse = await fetch(`${base_url}/api/v1/get_midprice?ticker=${ticker}`)
            const midpriceData = await midpriceResponse.text()
            setMidprice(midpriceData)
        }
        const interval = setInterval(fetchData, 1000)

        return () => {
            clearInterval(interval)
        }
    }, [ticker])

    return (
        <div>
            <h2>Data Table</h2>
            <table>
                <thead>
                    <tr>
                        <th>Candles</th>
                    </tr>
                </thead>
                <tbody>
                    {candles.map((candle, index) => (
                        <tr key={index}>
                            <td>{JSON.stringify(candle)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>

            <table>
                <thead>
                    <tr>
                        <th>Order Book</th>
                    </tr>
                </thead>
                <tbody>
                    {orderBook.bids.map((entry, index) => (
                        <tr key={index}>
                            <td>{JSON.stringify(entry)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>

            <table>
                <tbody>
                    {orderBook.asks.map((entry, index) => (
                        <tr key={index}>
                            <td>{JSON.stringify(entry)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>

            <table>
                <thead>
                    <tr>
                        <th>Trades</th>
                    </tr>
                </thead>
                <tbody>
                    {trades.map((trade, index) => (
                        <tr key={index}>
                            <td>{JSON.stringify(trade)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>

            <table>
                <thead>
                    <tr>
                        <th>Quotes</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{JSON.stringify(quotes)}</td>
                    </tr>
                </tbody>
            </table>

            <table>
                <thead>
                    <tr>
                        <th>Best Bid</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{JSON.stringify(bestBid)}</td>
                    </tr>
                </tbody>
            </table>

            <table>
                <thead>
                    <tr>
                        <th>Best Ask</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{JSON.stringify(bestAsk)}</td>
                    </tr>
                </tbody>
            </table>

            <table>
                <thead>
                    <tr>
                        <th>Midprice</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{midprice}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    )
}

export default TableComponent

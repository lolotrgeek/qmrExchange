from flask import Flask, jsonify, request



def API(sim):
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "hello"

    @app.route('/api/v1/candles')
    def candles():
        interval=request.args.get('interval')
        limit=request.args.get('limit', type=int)
        ticker=request.args.get('ticker')
        if(interval is None):
            interval = '15Min'
        if(limit is None):
            limit = 20
        if(ticker is None):
            ticker = 'XYZ'

        print(interval, limit, ticker)
        df_candles = sim.get_price_bars(ticker, bar_size=interval)
        return jsonify(df_candles.head(limit).to_json())

    @app.route('/api/v1/portfolio')
    def portfolio():
        mt_holdings = sim.get_portfolio_history('market_taker')
        mm_holdings = sim.get_portfolio_history('market_maker')
        return jsonify({'market_taker': mt_holdings.to_json(), 'market_maker': mm_holdings.to_json()})

    @app.route('/api/v1/trades')
    def trades():
        limit=request.args.get('limit', type=int)
        ticker=request.args.get('ticker')
        if(limit is None):
            limit = 20
        if(ticker is None):
            ticker = 'XYZ'
        trades = sim.trades.head(limit).to_json()
        return jsonify(trades)
    
    return app


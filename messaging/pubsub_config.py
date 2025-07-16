# messaging/pubsub_config.py

bootstrap_servers: localhost:9092
topics:
    stock_data: financial.stock.data
    analysis_requests: financial.analysis.requests
    analysis_results: financial.analysis.results
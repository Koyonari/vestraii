"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";
import StockChart from "@/components/StockChart";
import WatchlistBar from "@/components/WatchlistBar";

interface StockData {
  name: string;
  ticker: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  sentiment: {
    score: number;
    category: string;
    investment_score: number;
  };
  historical_data: Array<{ date: string; price: number }>;
  prediction: {
    data: Array<{ date: string; price: number }>;
    upper_bound: Array<{ date: string; price: number }>;
    lower_bound: Array<{ date: string; price: number }>;
  };
  last_updated: string;
}

export default function WatchlistPage() {
  const [selectedStock, setSelectedStock] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [currentPrice, setCurrentPrice] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string>("");

  // Fetch stock data function
  const fetchStockData = async (symbol: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/stocks?ticker=${symbol}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.error || `Failed to fetch data for ${symbol}`
        );
      }

      const data = await response.json();

      // Validate historical data exists
      if (!data.historical_data || data.historical_data.length === 0) {
        throw new Error(
          `No historical data available for ${symbol}. This stock may not have enough trading data.`
        );
      }

      // Calculate the current price (last historical price)
      const historicalData = data.historical_data;
      const lastPrice = historicalData[historicalData.length - 1].price;
      const prevPrice =
        historicalData[historicalData.length - 2]?.price || lastPrice;
      const change = lastPrice - prevPrice;
      const changePercent = (change / prevPrice) * 100;

      setStockData({
        name: data.name,
        ticker: data.ticker,
        currentPrice: lastPrice,
        change: change,
        changePercent: changePercent,
        sentiment: data.sentiment,
        historical_data: data.historical_data,
        prediction: data.prediction,
        last_updated: data.last_updated,
      });

      setCurrentPrice(lastPrice);
      setErrorMessage("");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Error fetching stock data";
      console.error("Error fetching stock data:", error);
      setErrorMessage(message);
      setStockData(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle stock selection from watchlist
  const handleStockSelect = (ticker: string) => {
    setSelectedStock(ticker);
  };

  // Fetch data when selected stock changes
  useEffect(() => {
    if (selectedStock) {
      fetchStockData(selectedStock);
    }
  }, [selectedStock]);

  // Format price to ensure proper decimal display
  const formatPrice = (price: number) => {
    return price.toFixed(2);
  };

  // Calculate price change
  const priceChange = {
    value: stockData ? stockData.changePercent.toFixed(2) : "0",
    percent: stockData ? stockData.changePercent.toFixed(2) : "0",
  };

  // Get sentiment category color
  const categoryColor =
    stockData?.sentiment.category === "Bullish"
      ? "text-green-500 font-medium"
      : stockData?.sentiment.category === "Bearish"
        ? "text-red-500 font-medium"
        : "text-gray-500 font-medium";

  // Calculate sentiment position (0-100%)
  const sentimentValue = ((stockData?.sentiment.score || 0) + 1) / 2;
  const sentimentPosition = `${sentimentValue * 100}%`;

  // Calculate investment score position
  const investmentValue = (stockData?.sentiment.investment_score || 50) / 100;
  const investmentPosition = `${investmentValue * 100}%`;

  // Get prediction data
  const lastPrediction = stockData?.prediction.data?.[
    stockData.prediction.data.length - 1
  ] || {
    date: "N/A",
    price: 0,
  };

  const bounds = {
    upper:
      stockData?.prediction.upper_bound?.[
        stockData.prediction.upper_bound.length - 1
      ]?.price.toFixed(2) || "0.00",
    lower:
      stockData?.prediction.lower_bound?.[
        stockData.prediction.lower_bound.length - 1
      ]?.price.toFixed(2) || "0.00",
  };

  const isPredictionPositive =
    lastPrediction.price > (stockData?.currentPrice || 0);
  const predictionChange = {
    value: stockData
      ? (
          ((lastPrediction.price - stockData.currentPrice) /
            stockData.currentPrice) *
          100
        ).toFixed(2)
      : "0",
    percent: stockData
      ? (
          ((lastPrediction.price - stockData.currentPrice) /
            stockData.currentPrice) *
          100
        ).toFixed(2)
      : "0",
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-copper dark:text-white">
        My Watchlist
      </h1>

      {/* Error Message Display */}
      {errorMessage && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">
            <strong>Unable to load stock:</strong> {errorMessage}
          </p>
          <p className="text-red-700 text-xs mt-2">
            This stock may not have sufficient data. Try selecting a different
            stock from the watchlist.
          </p>
        </div>
      )}

      {/* Main Layout: Watchlist | (Chart + Price Prediction + Sentiment below) */}
      <div className="flex gap-4 h-[calc(100vh-200px)]">
        {/* Left: Watchlist */}
        <WatchlistBar
          selectedTicker={selectedStock}
          onStockSelect={handleStockSelect}
        />

        {/* Right: Chart, Price Prediction, and Sentiment (Stacked) */}
        <div className="flex-1 flex flex-col gap-4 overflow-hidden">
          {/* Top Row: Chart | Price Prediction */}
          <div className="flex gap-4 flex-1 overflow-hidden">
            {/* Middle: Stock Chart */}
            <Card className="bg-background shadow-md flex-1 flex flex-col overflow-hidden">
              <CardHeader className="pb-2 flex-shrink-0">
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="text-xl font-bold">
                      {selectedStock || "Select a stock"}
                    </CardTitle>
                    {stockData && (
                      <div className="flex items-center gap-2 text-sm">
                        <span>{stockData.name}</span>
                        <span className="font-semibold">
                          ${formatPrice(currentPrice)}
                        </span>
                        <span
                          className={`flex items-center text-sm ${
                            Number(priceChange.value) > 0
                              ? "text-green-500"
                              : "text-red-500"
                          }`}
                        >
                          {Number(priceChange.value) > 0 ? (
                            <TrendingUp className="h-4 w-4 mr-1" />
                          ) : (
                            <TrendingDown className="h-4 w-4 mr-1" />
                          )}
                          {Number(priceChange.value) > 0 ? "+" : ""}
                          {priceChange.value} ({priceChange.percent}%)
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-6 flex-1 flex items-center justify-center overflow-hidden">
                {selectedStock ? (
                  !isLoading ? (
                    <StockChart
                      stockSymbol={selectedStock}
                      timeframe="1M"
                      onChartLoaded={() => {}}
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full w-full">
                      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-copper"></div>
                    </div>
                  )
                ) : (
                  <div className="text-center text-gray-500">
                    <p>Select a stock from the watchlist to view its chart</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Right: Price Prediction */}
            {stockData && stockData.prediction && (
              <Card className="bg-background shadow-md w-80 flex flex-col overflow-hidden">
                <CardHeader className="flex-shrink-0">
                  <CardTitle className="text-lg font-semibold">
                    Price Prediction
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-4 flex-1 flex flex-col justify-between overflow-hidden">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-500">
                        Current Price
                      </span>
                      {stockData && (
                        <span className="font-medium">
                          ${stockData.currentPrice.toFixed(2)}
                        </span>
                      )}
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-500">
                        Predicted Price <br />({lastPrediction.date})
                      </span>
                      <span className="font-medium">
                        ${lastPrediction.price.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-500">
                        Prediction
                        <br />
                        Change
                      </span>
                      <span
                        className={`font-medium ${
                          isPredictionPositive
                            ? "text-green-500"
                            : "text-red-500"
                        }`}
                      >
                        {isPredictionPositive ? "+" : ""}
                        {predictionChange.value} ({predictionChange.percent}%)
                      </span>
                    </div>
                    <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
                      <div className="text-sm text-gray-500 mb-2">
                        Confidence Interval
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Lower Bound</span>
                        <span className="font-medium">${bounds.lower}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Upper Bound</span>
                        <span className="font-medium">${bounds.upper}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Bottom Row: Sentiment Analysis (Same width as Chart + Price Prediction) */}
          {stockData && stockData.sentiment && (
            <Card className="bg-background shadow-md flex-shrink-0 flex flex-col">
              <CardHeader>
                <CardTitle className="text-lg font-semibold">
                  Sentiment Analysis
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6 flex flex-col justify-between">
                <div className="space-y-6">
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span>Bearish</span>
                      <span className={categoryColor}>
                        {stockData.sentiment.category}
                      </span>
                      <span>Bullish</span>
                    </div>
                    <div className="relative h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                      <div className="absolute w-full h-full flex items-center justify-center">
                        <div
                          className="absolute h-4 w-4 rounded-full bg-blue-500 shadow-md z-10"
                          style={{ left: sentimentPosition }}
                        ></div>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span>High Risk</span>
                      <span className="font-medium">
                        Investment Score: {stockData.sentiment.investment_score}
                        /100
                      </span>
                      <span>Low Risk</span>
                    </div>
                    <div className="relative h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                      <div
                        className="absolute h-full bg-gradient-to-r from-red-500 via-yellow-400 to-green-500 rounded-full"
                        style={{ width: "100%" }}
                      ></div>
                      <div className="absolute w-full h-full flex items-center justify-center">
                        <div
                          className="absolute h-4 w-4 rounded-full bg-white border-2 border-blue-500 shadow-md z-10"
                          style={{ left: investmentPosition }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

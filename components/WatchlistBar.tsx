"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";
import WatchlistBarSkeleton from "@/components/skeletons/WatchlistBarSkeleton";

interface WatchlistStock {
  ticker: string;
  name: string;
  current_price: number;
  prediction_change: number;
}

interface WatchlistBarProps {
  selectedTicker?: string;
  onStockSelect?: (ticker: string) => void;
}

export default function WatchlistBar({
  selectedTicker,
  onStockSelect,
}: WatchlistBarProps) {
  const [watchlist, setWatchlist] = useState<WatchlistStock[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchWatchlist = async () => {
      try {
        const response = await fetch("/api/stocks");
        if (!response.ok) throw new Error("Failed to fetch stocks");

        const stocks = await response.json();

        // Map API response to watchlist format
        const watchlistData: WatchlistStock[] = stocks.map(
          (stock: {
            ticker: string;
            name: string;
            sentiment?: { score?: number };
            prediction_change: number;
            current_price?: number;
          }) => ({
            ticker: stock.ticker,
            name: stock.name,
            current_price: stock.current_price || 0,
            prediction_change: stock.prediction_change || 0,
          })
        );

        setWatchlist(watchlistData);
      } catch (error) {
        console.error("Error fetching watchlist:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchWatchlist();
  }, []);

  if (isLoading) {
    return <WatchlistBarSkeleton />;
  }

  return (
    <Card className="bg-background shadow-md w-80 h-full flex flex-col">
      {/* Sticky Header */}
      <div className="sticky top-0 bg-background p-4 border-b border-border z-10">
        <h3 className="text-sm font-semibold text-foreground">Watchlist</h3>
      </div>

      {/* Scrollable Content */}
      <div className="overflow-y-auto flex-1 p-4 space-y-2">
        {watchlist.map((stock) => (
          <button
            key={stock.ticker}
            onClick={() => onStockSelect?.(stock.ticker)}
            className={`p-3 rounded cursor-pointer w-full transition-colors ${
              selectedTicker === stock.ticker
                ? "bg-primary/10 border border-primary"
                : "bg-muted hover:bg-muted/80 border border-transparent"
            }`}
          >
            <div className="flex items-center justify-between gap-2 mb-1">
              <span className="font-medium text-sm text-white truncate">
                {stock.ticker}
              </span>
              <span className="text-xs text-gray-300">
                ${stock.current_price.toFixed(2)}
              </span>
            </div>
            <div className="flex items-center justify-between gap-1">
              <span className="text-xs text-gray-400 text-left">
                {stock.name}
              </span>
              <div className="flex items-center gap-1 ml-auto">
                {stock.prediction_change > 0 ? (
                  <TrendingUp className="h-3 w-3 text-green-500" />
                ) : (
                  <TrendingDown className="h-3 w-3 text-red-500" />
                )}
                <span
                  className={`text-xs font-semibold ${
                    stock.prediction_change > 0
                      ? "text-green-500"
                      : "text-red-500"
                  }`}
                >
                  {stock.prediction_change > 0 ? "+" : ""}
                  {stock.prediction_change.toFixed(2)}%
                </span>
              </div>
            </div>
          </button>
        ))}
      </div>
    </Card>
  );
}

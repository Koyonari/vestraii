import { Skeleton } from "@/components/ui/skeleton";

export default function StockSentimentIndicatorSkeleton() {
  return (
    <div className="space-y-4 p-4 bg-white dark:bg-gray-900 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold mb-2">Sentiment Analysis</h3>

      {/* Sentiment Score Section */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span>Bearish</span>
          <Skeleton className="h-4 w-20" />
          <span>Bullish</span>
        </div>
        <div className="relative h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
          <Skeleton
            className="h-4 w-4 rounded-full absolute"
            style={{ left: "50%" }}
          />
        </div>
      </div>

      {/* Investment Score Section */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span>High Risk</span>
          <Skeleton className="h-4 w-32" />
          <span>Low Risk</span>
        </div>
        <div className="relative h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
          <div
            className="absolute h-full bg-gradient-to-r from-red-500 via-yellow-400 to-green-500 rounded-full"
            style={{ width: "100%" }}
          ></div>
          <Skeleton
            className="h-4 w-4 rounded-full absolute border-2"
            style={{ left: "50%" }}
          />
        </div>
      </div>
    </div>
  );
}

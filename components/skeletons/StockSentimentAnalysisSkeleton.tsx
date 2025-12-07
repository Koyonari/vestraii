import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

export default function StockSentimentAnalysisSkeleton() {
  return (
    <Card className="bg-background shadow-md flex-grow flex-col flex w-full">
      <CardHeader>
        <CardTitle className="text-lg font-semibold">
          Sentiment Analysis
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6 flex-grow flex flex-col justify-between">
        {/* Sentiment Score */}
        <div className="space-y-6 flex-grow">
          {/* Sentiment Score Section */}
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span>Bearish</span>
              <Skeleton className="h-4 w-20" />
              <span>Bullish</span>
            </div>
            <div className="relative h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <Skeleton className="h-4 w-4 rounded-full absolute" style={{ left: '50%' }} />
            </div>
          </div>

          {/* Investment Score Section */}
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span>High Risk</span>
              <Skeleton className="h-4 w-32" />
              <span>Low Risk</span>
            </div>
            <div className="relative h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div
                className="absolute h-full bg-gradient-to-r from-red-500 via-yellow-400 to-green-500 rounded-full"
                style={{ width: '100%' }}
              ></div>
              <Skeleton className="h-4 w-4 rounded-full absolute border-2" style={{ left: '50%' }} />
            </div>
          </div>
        </div>

        {/* Spacer div to push content to top */}
        <div className="mt-auto pt-4"></div>
      </CardContent>
    </Card>
  )
}

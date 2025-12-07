import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

export default function PredictionConfidenceCardSkeleton() {
  return (
    <Card className="bg-background shadow-md flex-grow flex w-full">
      <CardHeader>
        <CardTitle className="text-lg font-semibold">Price Prediction</CardTitle>
      </CardHeader>
      <CardContent className="p-4 w-full">
        <div className="space-y-4">
          {/* Current Price Row */}
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-500">Current Price</span>
            <Skeleton className="h-5 w-20" />
          </div>
          
          {/* Predicted Price Row */}
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-500">
              Predicted Price <br />(Date)
            </span>
            <Skeleton className="h-5 w-24" />
          </div>
          
          {/* Prediction Change Row */}
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-500">
              Prediction<br />Change
            </span>
            <Skeleton className="h-5 w-28" />
          </div>
          
          {/* Divider and Confidence Interval Section */}
          <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
            <div className="text-sm text-gray-500 mb-2">Confidence Interval</div>
            
            {/* Lower Bound */}
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm">Lower Bound</span>
              <Skeleton className="h-5 w-20" />
            </div>
            
            {/* Upper Bound */}
            <div className="flex justify-between items-center">
              <span className="text-sm">Upper Bound</span>
              <Skeleton className="h-5 w-20" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

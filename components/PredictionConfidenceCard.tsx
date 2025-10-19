import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

interface PredictionData {
  date: string
  price: number
}

interface Prediction {
  data: PredictionData[]
  upper_bound: PredictionData[]
  lower_bound: PredictionData[]
}

interface PricePredictionProps {
  currentPrice: number
  prediction: Prediction
}

export default function PricePrediction({ currentPrice, prediction }: PricePredictionProps) {
  // Get the last prediction date and price
  const lastIndex = prediction.data.length - 1
  const lastPrediction = {
    date: new Date(prediction.data[lastIndex].date).toLocaleDateString(),
    price: prediction.data[lastIndex].price,
  }

  // Calculate the prediction change percentage
  const change = lastPrediction.price - currentPrice
  const percentChange = (change / currentPrice) * 100
  const predictionChange = {
    value: change.toFixed(2),
    percent: percentChange.toFixed(2),
  }

  // Calculate the upper and lower bounds
  const lastBoundIndex = prediction.upper_bound.length - 1
  const bounds = {
    upper: prediction.upper_bound[lastBoundIndex].price.toFixed(2),
    lower: prediction.lower_bound[lastBoundIndex].price.toFixed(2),
  }

  // Determine if the prediction is positive or negative
  const isPredictionPositive = lastPrediction.price >= currentPrice

  return (
    <Card className="bg-background shadow-md">
      <CardHeader>
        <CardTitle className="text-lg font-semibold">Price Prediction</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-500">Current Price</span>
            <span className="font-medium">${currentPrice.toFixed(2)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-500">
              Predicted Price ({lastPrediction.date})
            </span>
            <span className="font-medium">${lastPrediction.price.toFixed(2)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-500">Prediction Change</span>
            <span
              className={`font-medium ${
                isPredictionPositive ? 'text-green-500' : 'text-red-500'
              }`}
            >
              {isPredictionPositive ? '+' : ''}
              {predictionChange.value} ({predictionChange.percent}%)
            </span>
          </div>
          <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
            <div className="text-sm text-gray-500 mb-2">Confidence Interval</div>
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
  )
}

'use client'

import { useState, useMemo } from 'react'
import { TrendingUp, TrendingDown, ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function PredictionsList() {
  const predictions = [
    {
      id: 1,
      company: 'Apple',
      symbol: 'AAPL',
      prediction: 10,
      direction: 'increase',
      timeframe: '7 days',
      timestamp: '2h ago',
      logoClass: 'bg-gray-200',
    },
    {
      id: 2,
      company: 'Apple',
      symbol: 'AAPL',
      prediction: 5,
      direction: 'decrease',
      timeframe: '7 days',
      timestamp: '1d ago',
      logoClass: 'bg-gray-200',
    },
    {
      id: 3,
      company: 'Amazon',
      symbol: 'AMZN',
      prediction: 8,
      direction: 'increase',
      timeframe: '7 days',
      timestamp: '2d ago',
      logoClass: 'bg-gray-100',
    },
    {
      id: 4,
      company: 'Microsoft',
      symbol: 'MSFT',
      prediction: 6,
      direction: 'increase',
      timeframe: '7 days',
      timestamp: '3d ago',
      logoClass: 'bg-green-100',
    },
    {
      id: 5,
      company: 'Tesla',
      symbol: 'TSLA',
      prediction: 12,
      direction: 'decrease',
      timeframe: '7 days',
      timestamp: '4d ago',
      logoClass: 'bg-red-100',
    },
  ]

  // Pagination logic
  const itemsPerPage = 3
  const [currentPage, setCurrentPage] = useState(1)

  const totalPages = useMemo(
    () => Math.ceil(predictions.length / itemsPerPage),
    [predictions.length]
  )

  const paginatedPredictions = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage
    const end = start + itemsPerPage
    return predictions.slice(start, end)
  }, [currentPage, predictions])

  const nextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1)
    }
  }

  const prevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1)
    }
  }

  return (
    <div className="h-[360px] flex flex-col justify-between">
      <div className="space-y-4 overflow-y-auto">
        {paginatedPredictions.map((prediction) => (
          <div
            key={prediction.id}
            className="flex items-center gap-4 p-3 border-b border-copper/20 last:border-none"
          >
            <div
              className={`${prediction.logoClass} h-10 w-10 rounded-full flex items-center justify-center`}
            >
              <span className="text-sm font-semibold">{prediction.symbol.substring(0, 1)}</span>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                {prediction.direction === 'increase' ? (
                  <TrendingUp className="h-4 w-4 text-green-500" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-500" />
                )}
                <span className="font-medium">
                  {prediction.company} stock is predicted to{' '}
                  <span
                    className={
                      prediction.direction === 'increase' ? 'text-green-500' : 'text-red-500'
                    }
                  >
                    {prediction.direction}
                  </span>{' '}
                  by {prediction.prediction}% in the next {prediction.timeframe}
                </span>
              </div>
              <div className="text-xs text-gray-500 mt-1">{prediction.timestamp}</div>
            </div>
          </div>
        ))}
      </div>
      {/* Pagination Controls */}
      <div className="flex justify-between items-center mt-4 pt-2 border-t">
        <Button variant="outline" size="sm" disabled={currentPage === 1} onClick={prevPage}>
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <span className="text-sm">
          Page {currentPage} of {totalPages}
        </span>
        <Button variant="outline" size="sm" disabled={currentPage === totalPages} onClick={nextPage}>
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}

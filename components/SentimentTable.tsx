'use client'

import { useState, useEffect, useMemo } from 'react'
import { TrendingUp, TrendingDown, ArrowUpDown, ChevronDown, ChevronUp } from 'lucide-react'
import { Button } from '@/components/ui/button'
import Papa from 'papaparse'

interface SentimentItem {
  rank: number
  ticker: string
  name: string
  investment_score: number
  avg_sentiment: number
  news_count: number
}

type SortColumn = keyof SentimentItem
type SortDirection = 'asc' | 'desc'

export default function SentimentTable() {
  const [sentimentData, setSentimentData] = useState<SentimentItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [sortColumn, setSortColumn] = useState<SortColumn>('rank')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')
  const [expanded, setExpanded] = useState(false)
  const initialDisplayCount = 10

  const loadCsvData = async () => {
    try {
      const response = await fetch('/backend/reports/investment_ranking.csv')
      const csvText = await response.text()

      const results = Papa.parse(csvText, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true,
      })

      setSentimentData(results.data as SentimentItem[])
    } catch (error) {
      console.error('Error loading CSV:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadCsvData()
  }, [])

  // Another round of sorting just in case the data is not sorted correctly
  const sortData = (column: SortColumn) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(column)
      setSortDirection('asc')
    }

    setSentimentData((prev) => {
      const sorted = [...prev]
      const multiplier = sortDirection === 'asc' ? 1 : -1
      sorted.sort((a, b) => {
        return (a[column] < b[column] ? -1 : 1) * multiplier
      })
      return sorted
    })
  }

  const displayedData = useMemo(() => {
    return expanded ? sentimentData : sentimentData.slice(0, initialDisplayCount)
  }, [expanded, sentimentData])

  const toggleExpand = () => {
    setExpanded(!expanded)
  }

  const headers = ['Rank', 'Symbol', 'Company', 'Sentiment Score', 'Sentiment', 'Articles']
  const headerKeys: SortColumn[] = ['rank', 'ticker', 'name', 'investment_score', 'avg_sentiment', 'news_count']

  return (
    <div className="w-full">
      {isLoading ? (
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
        </div>
      ) : (
        <div className="rounded-md border">
          <div className="relative w-full overflow-auto">
            <table className="w-full caption-bottom text-sm">
              <thead className="[&_tr]:border-b">
                <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                  {headers.map((header, index) => (
                    <th
                      key={header}
                      className="h-12 px-4 text-left align-middle font-medium text-muted-foreground"
                    >
                      <div
                        className="flex items-center space-x-2 cursor-pointer"
                        onClick={() => sortData(headerKeys[index])}
                      >
                        <span>{header}</span>
                        <ArrowUpDown className="h-4 w-4" />
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="[&_tr:last-child]:border-0">
                {displayedData.map((item) => (
                  <tr
                    key={item.ticker}
                    className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted"
                  >
                    <td className="p-4 align-middle">{item.rank}</td>
                    <td className="p-4 align-middle font-medium">{item.ticker}</td>
                    <td className="p-4 align-middle">{item.name}</td>
                    <td className="p-4 align-middle">
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-secondary rounded-full h-2">
                          <div
                            className="bg-primary h-2 rounded-full"
                            style={{ width: `${item.investment_score}%` }}
                          />
                        </div>
                        <span>{item.investment_score.toFixed(1)}</span>
                      </div>
                    </td>
                    <td className="p-4 align-middle">
                      <div className="flex items-center gap-2">
                        {item.avg_sentiment > 0 ? (
                          <TrendingUp className="h-4 w-4 text-green-500" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-red-500" />
                        )}
                        <span
                          className={
                            item.avg_sentiment > 0 ? 'text-green-500' : 'text-red-500'
                          }
                        >
                          {(item.avg_sentiment * 100).toFixed(2)}%
                        </span>
                      </div>
                    </td>
                    <td className="p-4 align-middle">{item.news_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex justify-center p-4">
            <Button variant="outline" onClick={toggleExpand}>
              {expanded
                ? 'Show Less'
                : `Show ${sentimentData.length - initialDisplayCount} More`}
              {!expanded ? (
                <ChevronDown className="h-4 w-4 ml-2" />
              ) : (
                <ChevronUp className="h-4 w-4 ml-2" />
              )}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

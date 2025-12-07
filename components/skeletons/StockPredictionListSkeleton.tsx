import { Skeleton } from "@/components/ui/skeleton";

export default function StockPredictionListSkeleton() {
  return (
    <div className="h-[360px] flex flex-col justify-between w-full">
      <div className="space-y-4 overflow-y-auto">
        {/* Prediction Item 1 */}
        <div className="flex items-center gap-4 p-3 border-b border-copper/20">
          <Skeleton className="h-10 w-10 rounded-full flex-shrink-0" />
          <div className="flex-1">
            <Skeleton className="h-4 w-full mb-2" />
            <Skeleton className="h-3 w-24" />
          </div>
        </div>

        {/* Prediction Item 2 */}
        <div className="flex items-center gap-4 p-3 border-b border-copper/20">
          <Skeleton className="h-10 w-10 rounded-full flex-shrink-0" />
          <div className="flex-1">
            <Skeleton className="h-4 w-full mb-2" />
            <Skeleton className="h-3 w-24" />
          </div>
        </div>

        {/* Prediction Item 3 */}
        <div className="flex items-center gap-4 p-3 last:border-none">
          <Skeleton className="h-10 w-10 rounded-full flex-shrink-0" />
          <div className="flex-1">
            <Skeleton className="h-4 w-full mb-2" />
            <Skeleton className="h-3 w-24" />
          </div>
        </div>
      </div>

      {/* Pagination Controls */}
      <div className="flex justify-between items-center mt-4 pt-2 border-t">
        <Skeleton className="h-8 w-8" />
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-8 w-8" />
      </div>
    </div>
  );
}

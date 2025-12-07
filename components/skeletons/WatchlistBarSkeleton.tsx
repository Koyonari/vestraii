import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function WatchlistBarSkeleton() {
  return (
    <Card className="bg-background shadow-md w-80 h-full flex flex-col">
      {/* Sticky Header */}
      <div className="sticky top-0 bg-background p-4 border-b border-border z-10">
        <h3 className="text-sm font-semibold text-foreground">Watchlist</h3>
      </div>

      {/* Scrollable Content */}
      <div className="overflow-y-auto flex-1 p-4 space-y-2">
        {Array.from({ length: 8 }).map((_, index) => (
          <div
            key={index}
            className="p-3 rounded w-full bg-muted border border-transparent"
          >
            <div className="flex items-center justify-between gap-2 mb-1">
              <Skeleton className="h-4 w-12" />
              <Skeleton className="h-4 w-16" />
            </div>
            <div className="flex items-center justify-between gap-1">
              <Skeleton className="h-3 w-32" />
              <div className="flex items-center gap-1 ml-auto">
                <Skeleton className="h-3 w-3 rounded-full" />
                <Skeleton className="h-3 w-10" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

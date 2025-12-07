import { Skeleton } from "@/components/ui/skeleton";

export default function SentimentTableSkeleton() {
  const headers = [
    "Rank",
    "Symbol",
    "Company",
    "Sentiment Score",
    "Prediction Change",
    "Articles",
  ];
  const initialDisplayCount = 10;

  return (
    <div className="w-full">
      <div className="rounded-md border">
        <div className="relative w-full overflow-auto">
          <table className="w-full caption-bottom text-sm">
            <thead className="[&_tr]:border-b">
              <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                {headers.map((header) => (
                  <th
                    key={header}
                    className="h-12 px-4 text-left align-middle font-medium text-muted-foreground"
                  >
                    <div className="flex items-center space-x-2 cursor-pointer">
                      <span>{header}</span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="[&_tr:last-child]:border-0">
              {Array.from({ length: initialDisplayCount }).map((_, index) => (
                <tr
                  key={index}
                  className="border-b transition-colors hover:bg-muted/50"
                >
                  {/* Rank */}
                  <td className="p-4 align-middle">
                    <Skeleton className="h-4 w-6" />
                  </td>
                  {/* Symbol */}
                  <td className="p-4 align-middle">
                    <Skeleton className="h-4 w-12" />
                  </td>
                  {/* Company Name */}
                  <td className="p-4 align-middle">
                    <Skeleton className="h-4 w-40" />
                  </td>
                  {/* Sentiment Score */}
                  <td className="p-4 align-middle">
                    <div className="flex items-center gap-2">
                      <Skeleton className="w-24 h-2 rounded-full" />
                      <Skeleton className="h-4 w-8" />
                    </div>
                  </td>
                  {/* Prediction Change */}
                  <td className="p-4 align-middle">
                    <div className="flex items-center gap-2">
                      <Skeleton className="h-4 w-4" />
                      <Skeleton className="h-4 w-12" />
                    </div>
                  </td>
                  {/* Articles Count */}
                  <td className="p-4 align-middle">
                    <Skeleton className="h-4 w-8" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex justify-center p-4">
          <Skeleton className="h-9 w-32" />
        </div>
      </div>
    </div>
  );
}

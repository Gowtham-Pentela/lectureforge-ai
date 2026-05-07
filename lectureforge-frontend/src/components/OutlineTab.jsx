import React from "react";
import { Clock3 } from "lucide-react";

export default function OutlineTab({ outline }) {
  return (
    <div className="grid gap-4">
      {outline?.map((item, index) => (
        <article
          key={`${item.title}-${index}`}
          className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div className="mb-3 flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
            <div>
              <h3 className="text-lg font-bold text-slate-900">{item.title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">{item.summary}</p>
            </div>

            <div className="inline-flex shrink-0 items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-700">
              <Clock3 size={15} />
              {item.start_time} to {item.end_time}
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}

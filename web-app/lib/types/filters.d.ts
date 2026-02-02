import "@bazza-ui/filters";

declare module "@bazza-ui/filters" {
  interface ColumnMeta {
    number?: {
      unit?: "seconds" | "minutes" | "hours";
    };
  }
}

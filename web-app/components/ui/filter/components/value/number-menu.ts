import type { MenuMiddleware } from "@bazza-ui/menu/middleware";
import type {
  Column,
  DataTableFilterActions,
  NumberFilterOperator,
} from "@bazza-ui/filters";
import { SubmenuDef } from "@bazza-ui/dropdown-menu";
import { parseDurationToUnit } from "@/lib/utils";

export function createNumberFilterMiddleware<TData>({
  column,
  actions,
}: {
  column: Column<TData, "number">;
  actions: DataTableFilterActions;
}): MenuMiddleware {
  return {
    transformNodes: (context: any) => {
      const { query, mode, createNode } = context;

      if (mode !== "search" || !query?.trim()) return [];

      // support different units

      const unit = (column as any).meta?.number?.unit as
        | "seconds"
        | "minutes"
        | "hours"
        | undefined;

      // default if missing
      const baseUnit = unit ?? "minutes";

      const n = parseDurationToUnit(query, baseUnit);
      if (n === null) return [];

      // const n = Number(query);
      // if (!Number.isFinite(n)) return [];

      // use meta for label (for now, just show unit text)
      // const unitLabel = column.meta?.number?.unit ?? "";
      // const pretty = unitLabel ? `${n} ${unitLabel}` : `${n}`;

      const unitLabel = unit === "minutes" ? "min" : unit;

      const pretty = `${n} ${unitLabel}`;

      const apply = (operator: NumberFilterOperator) => {
        actions.batch((tx: any) => {
          tx.setFilterValue(column, [n]);
          tx.setFilterOperator(column.id, operator);
        });
      };

      const items: Array<[NumberFilterOperator, string]> = [
        ["is", `is ${pretty}`],
        ["is not", `is not ${pretty}`],
        ["is greater than", `is greater than ${pretty}`],
        [
          "is greater than or equal to",
          `is greater than or equal to ${pretty}`,
        ],
        ["is less than", `is less than ${pretty}`],
        ["is less than or equal to", `is less than or equal to ${pretty}`],
      ];

      return items.map(([op, label]) =>
        createNode({
          kind: "item",
          id: `${column.id}-number-${op}-${query}`,
          label,
          keywords: [query],
          onSelect: () => apply(op),
        })
      );
    },
  };
}

export function createNumberUnitMenu<TData>({
  column,
  actions,
}: {
  column: Column<TData, "number">;
  actions: DataTableFilterActions;
}): SubmenuDef {
  return {
    kind: "submenu",
    id: column.id,
    icon: column.icon,
    label: column.displayName,
    inputPlaceholder: `Enter ${column.displayName.toLowerCase()}...`,
    defaults: {
      item: { closeOnSelect: true },
    },
    middleware: createNumberFilterMiddleware({ column, actions }),
  };
}
